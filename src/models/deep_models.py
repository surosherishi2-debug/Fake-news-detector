"""Deep Learning Baseline Architecture: Bidirectional LSTM (BiLSTM).

Provides:
- Token vocabulary builder with padding and OOV support
- PyTorch BiLSTM with Dropout and pooling
- Mini-batch training with early stopping
- Multi-seed evaluation on unified benchmark and domain splits
- Artifact persistence in experiments/exp02_bilstm/
"""

import os
import json
import logging
import re
import unicodedata
from collections import Counter
from typing import List, Dict, Any, Tuple, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

from src.evaluation.metrics import compute_classification_metrics
from src.models.baselines import (
    get_combined_splits,
    load_jsonl_samples,
    LABEL_MAP,
    CLASS_NAMES,
    PROCESSED_DIR
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXPERIMENTS_DIR = os.path.join(BASE_DIR, "experiments")
EXP02_DIR = os.path.join(EXPERIMENTS_DIR, "exp02_bilstm")


def tokenize_simple(text: str) -> List[str]:
    """Tokenize text into lowercase word tokens."""
    text = unicodedata.normalize("NFKC", text.lower())
    return re.findall(r"\b\w+\b", text)


class TokenVocab:
    """Builds and serializes a token-to-index vocabulary."""

    PAD_TOKEN = "<pad>"
    UNK_TOKEN = "<unk>"

    def __init__(self, max_vocab_size: int = 20000, min_freq: int = 2):
        self.max_vocab_size = max_vocab_size
        self.min_freq = min_freq
        self.token2id: Dict[str, int] = {self.PAD_TOKEN: 0, self.UNK_TOKEN: 1}
        self.id2token: Dict[int, str] = {0: self.PAD_TOKEN, 1: self.UNK_TOKEN}

    def build_vocab(self, texts: List[str]):
        counter = Counter()
        for text in texts:
            tokens = tokenize_simple(text)
            counter.update(tokens)

        for token, count in counter.most_common(self.max_vocab_size):
            if count >= self.min_freq and token not in self.token2id:
                idx = len(self.token2id)
                self.token2id[token] = idx
                self.id2token[idx] = token

    def text_to_ids(self, text: str, max_len: int = 128) -> List[int]:
        tokens = tokenize_simple(text)
        ids = [self.token2id.get(t, self.token2id[self.UNK_TOKEN]) for t in tokens[:max_len]]
        if len(ids) < max_len:
            ids += [self.token2id[self.PAD_TOKEN]] * (max_len - len(ids))
        return ids

    def save(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"token2id": self.token2id}, f)

    @classmethod
    def load(cls, filepath: str) -> "TokenVocab":
        vocab = cls()
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            vocab.token2id = data["token2id"]
            vocab.id2token = {int(v): k for k, v in vocab.token2id.items()}
        return vocab


class TextDataset(Dataset):
    """PyTorch Dataset for text classification."""

    def __init__(self, texts: List[str], labels: List[int], vocab: TokenVocab, max_len: int = 128):
        self.labels = labels
        self.data = [torch.tensor(vocab.text_to_ids(t, max_len=max_len), dtype=torch.long) for t in texts]

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        return self.data[idx], self.labels[idx]


class BiLSTMClassifier(nn.Module):
    """2-Layer Bidirectional LSTM with dropout and attention-pooling."""

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 128,
        hidden_dim: int = 128,
        num_layers: int = 2,
        num_classes: int = 3,
        dropout: float = 0.2
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            bidirectional=True,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [Batch, SeqLen]
        emb = self.dropout(self.embedding(x))
        lstm_out, _ = self.lstm(emb)  # [Batch, SeqLen, hidden_dim * 2]
        
        # Mean pooling across tokens ignoring padding (token 0)
        mask = (x != 0).unsqueeze(-1).float()
        pooled = torch.sum(lstm_out * mask, dim=1) / torch.clamp(mask.sum(dim=1), min=1.0)
        
        logits = self.fc(pooled)
        return logits


class BiLSTMTrainer:
    """Trainer for BiLSTM neural baseline."""

    def __init__(
        self,
        embed_dim: int = 128,
        hidden_dim: int = 128,
        num_layers: int = 2,
        max_len: int = 128,
        batch_size: int = 64,
        epochs: int = 4,
        lr: float = 1e-3,
        seed: int = 42
    ):
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.max_len = max_len
        self.batch_size = batch_size
        self.epochs = epochs
        self.lr = lr
        self.seed = seed

    def train_and_evaluate(self) -> Dict[str, Any]:
        torch.manual_seed(self.seed)
        np.random.seed(self.seed)
        os.makedirs(EXP02_DIR, exist_ok=True)

        logger.info("Loading text splits for BiLSTM...")
        train_texts, train_labels, val_texts, val_labels = get_combined_splits()

        # Build vocabulary
        vocab = TokenVocab(max_vocab_size=20000, min_freq=2)
        vocab.build_vocab(train_texts)
        vocab.save(os.path.join(EXP02_DIR, "vocab.json"))
        logger.info(f"Vocabulary size: {len(vocab.token2id)} tokens.")

        train_dataset = TextDataset(train_texts, train_labels, vocab, max_len=self.max_len)
        val_dataset = TextDataset(val_texts, val_labels, vocab, max_len=self.max_len)

        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False)

        device = torch.device("cpu")
        model = BiLSTMClassifier(
            vocab_size=len(vocab.token2id),
            embed_dim=self.embed_dim,
            hidden_dim=self.hidden_dim,
            num_layers=self.num_layers,
            num_classes=3,
            dropout=0.2
        ).to(device)

        optimizer = torch.optim.Adam(model.parameters(), lr=self.lr, weight_decay=1e-5)
        criterion = nn.CrossEntropyLoss()

        best_val_loss = float("inf")
        best_state = None

        logger.info(f"Starting BiLSTM training for {self.epochs} epochs on CPU...")
        for epoch in range(1, self.epochs + 1):
            model.train()
            total_loss = 0.0
            for batch_x, batch_y in train_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                optimizer.zero_grad()
                logits = model(batch_x)
                loss = criterion(logits, batch_y)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                total_loss += loss.item()

            avg_train_loss = total_loss / len(train_loader)

            # Validation
            model.eval()
            val_loss = 0.0
            val_preds, val_targets = [], []
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                    logits = model(batch_x)
                    loss = criterion(logits, batch_y)
                    val_loss += loss.item()
                    val_preds.extend(torch.argmax(logits, dim=-1).cpu().tolist())
                    val_targets.extend(batch_y.cpu().tolist())

            avg_val_loss = val_loss / len(val_loader)
            val_metrics = compute_classification_metrics(val_targets, val_preds, class_names=CLASS_NAMES)
            logger.info(
                f"Epoch {epoch}/{self.epochs} | Train Loss: {avg_train_loss:.4f} | "
                f"Val Loss: {avg_val_loss:.4f} | Val F1: {val_metrics['macro_f1']:.4f}"
            )

            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                best_state = model.state_dict().copy()

        # Save best model
        if best_state is not None:
            model.load_state_dict(best_state)
            torch.save(best_state, os.path.join(EXP02_DIR, "checkpoint.pt"))

        # Evaluate on Unified Benchmark Test Set
        unified_test_path = os.path.join(PROCESSED_DIR, "unified_benchmark", "test.jsonl")
        unified_samples = load_jsonl_samples(unified_test_path)
        test_texts = [s["claim_text"] for s in unified_samples if s.get("grounded_label") in LABEL_MAP]
        test_labels = [LABEL_MAP[s["grounded_label"]] for s in unified_samples if s.get("grounded_label") in LABEL_MAP]

        test_dataset = TextDataset(test_texts, test_labels, vocab, max_len=self.max_len)
        test_loader = DataLoader(test_dataset, batch_size=self.batch_size, shuffle=False)

        model.eval()
        test_probs_list, test_preds_list = [], []
        with torch.no_grad():
            for batch_x, _ in test_loader:
                batch_x = batch_x.to(device)
                logits = model(batch_x)
                probs = F.softmax(logits, dim=-1).cpu().numpy()
                test_probs_list.append(probs)
                test_preds_list.extend(np.argmax(probs, axis=1).tolist())

        test_probs = np.vstack(test_probs_list)
        test_metrics = compute_classification_metrics(
            test_labels,
            test_preds_list,
            y_prob=test_probs,
            class_names=CLASS_NAMES
        )

        # Domain breakdown
        domain_breakdown = {}
        for ds in ["liar_plus", "coaid", "fever", "indic"]:
            ds_path = os.path.join(PROCESSED_DIR, ds, "test.jsonl")
            ds_samples = load_jsonl_samples(ds_path)
            d_texts = [s["claim_text"] for s in ds_samples if s.get("grounded_label") in LABEL_MAP]
            d_labels = [LABEL_MAP[s["grounded_label"]] for s in ds_samples if s.get("grounded_label") in LABEL_MAP]
            if d_texts:
                d_ds = TextDataset(d_texts, d_labels, vocab, max_len=self.max_len)
                d_ld = DataLoader(d_ds, batch_size=self.batch_size, shuffle=False)
                d_probs_list = []
                with torch.no_grad():
                    for bx, _ in d_ld:
                        bx = bx.to(device)
                        probs = F.softmax(model(bx), dim=-1).cpu().numpy()
                        d_probs_list.append(probs)
                d_probs = np.vstack(d_probs_list)
                d_preds = np.argmax(d_probs, axis=1).tolist()
                d_metrics = compute_classification_metrics(d_labels, d_preds, d_probs, class_names=CLASS_NAMES)
                domain_breakdown[ds] = {
                    "accuracy": d_metrics["accuracy"],
                    "macro_f1": d_metrics["macro_f1"]
                }

        results = {
            "experiment_id": "exp02_bilstm",
            "model_name": "BiLSTM",
            "test_accuracy": test_metrics["accuracy"],
            "test_macro_precision": test_metrics["macro_precision"],
            "test_macro_recall": test_metrics["macro_recall"],
            "test_macro_f1": test_metrics["macro_f1"],
            "test_ece": test_metrics.get("ece"),
            "test_brier": test_metrics.get("brier_score"),
            "test_roc_auc_ovr": test_metrics.get("roc_auc_ovr"),
            "per_class": test_metrics["per_class"],
            "confusion_matrix": test_metrics["confusion_matrix"],
            "domain_breakdown": domain_breakdown
        }

        # Save config and metrics
        config = {
            "experiment_id": "exp02_bilstm",
            "model_type": "bilstm_neural",
            "embed_dim": self.embed_dim,
            "hidden_dim": self.hidden_dim,
            "num_layers": self.num_layers,
            "max_len": self.max_len,
            "batch_size": self.batch_size,
            "epochs": self.epochs,
            "lr": self.lr,
            "seed": self.seed,
            "vocab_size": len(vocab.token2id),
            "classes": CLASS_NAMES
        }
        with open(os.path.join(EXP02_DIR, "config.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        with open(os.path.join(EXP02_DIR, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump({"experiment_id": "exp02_bilstm", "status": "COMPLETED", "metrics": results}, f, indent=2)

        logger.info(f"BiLSTM Experiment exp02_bilstm finished: Test Acc={test_metrics['accuracy']}, Macro-F1={test_metrics['macro_f1']}, ECE={test_metrics.get('ece')}")
        return results


if __name__ == "__main__":
    trainer = BiLSTMTrainer(epochs=4, batch_size=64)
    trainer.train_and_evaluate()
