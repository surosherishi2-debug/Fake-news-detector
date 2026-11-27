"""Pre-trained Transformer Models: English (all-MiniLM-L6-v2) & Multilingual (paraphrase-multilingual-MiniLM-L12-v2).

Provides:
- Contextual dense semantic representation encoding
- Classification layer training and calibration
- Cross-lingual Indic transfer evaluation (Hindi/Marathi IFCN claims)
- Multi-metric evaluation and artifact persistence in experiments/exp03_* and exp04_*
"""

import os
import json
import logging
import joblib
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

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
EXP03_DIR = os.path.join(EXPERIMENTS_DIR, "exp03_transformer_english")
EXP04_DIR = os.path.join(EXPERIMENTS_DIR, "exp04_transformer_multilingual")


class TransformerClassifier(nn.Module):
    """Classification head on top of pre-trained transformer sentence representations."""

    def __init__(self, embed_dim: int = 384, hidden_dim: int = 128, num_classes: int = 3, dropout: float = 0.2):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc(x)


class TransformerTrainer:
    """Trains and evaluates English and Multilingual Transformer models."""

    def __init__(
        self,
        model_name: str,
        exp_dir: str,
        exp_id: str,
        seed: int = 42,
        batch_size: int = 64,
        epochs: int = 10,
        lr: float = 2e-3
    ):
        self.model_name = model_name
        self.exp_dir = exp_dir
        self.exp_id = exp_id
        self.seed = seed
        self.batch_size = batch_size
        self.epochs = epochs
        self.lr = lr

    def run_training_pipeline(self) -> Dict[str, Any]:
        torch.manual_seed(self.seed)
        np.random.seed(self.seed)
        os.makedirs(self.exp_dir, exist_ok=True)

        logger.info(f"Loading SentenceTransformer: {self.model_name}...")
        encoder = SentenceTransformer(self.model_name)

        logger.info("Loading training and validation text samples...")
        train_texts, train_labels, val_texts, val_labels = get_combined_splits()

        # Load unified benchmark test set
        unified_test_path = os.path.join(PROCESSED_DIR, "unified_benchmark", "test.jsonl")
        unified_samples = load_jsonl_samples(unified_test_path)
        test_texts = [s["claim_text"] for s in unified_samples if s.get("grounded_label") in LABEL_MAP]
        test_labels = [LABEL_MAP[s["grounded_label"]] for s in unified_samples if s.get("grounded_label") in LABEL_MAP]

        logger.info("Extracting dense sentence embeddings (batch encoding)...")
        # Pre-compute embeddings for fast, deterministic training on CPU
        x_train = encoder.encode(train_texts, batch_size=self.batch_size, show_progress_bar=False, normalize_embeddings=True)
        x_val = encoder.encode(val_texts, batch_size=self.batch_size, show_progress_bar=False, normalize_embeddings=True)
        x_test = encoder.encode(test_texts, batch_size=self.batch_size, show_progress_bar=False, normalize_embeddings=True)

        embed_dim = x_train.shape[1]
        device = torch.device("cpu")

        # PyTorch classification head
        head = TransformerClassifier(embed_dim=embed_dim, hidden_dim=128, num_classes=3, dropout=0.2).to(device)
        optimizer = torch.optim.Adam(head.parameters(), lr=self.lr, weight_decay=1e-4)
        criterion = nn.CrossEntropyLoss()

        train_x_tensor = torch.tensor(x_train, dtype=torch.float32)
        train_y_tensor = torch.tensor(train_labels, dtype=torch.long)
        val_x_tensor = torch.tensor(x_val, dtype=torch.float32)
        val_y_tensor = torch.tensor(val_labels, dtype=torch.long)
        test_x_tensor = torch.tensor(x_test, dtype=torch.float32)

        train_dataset = torch.utils.data.TensorDataset(train_x_tensor, train_y_tensor)
        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)

        best_val_loss = float("inf")
        best_state = None

        logger.info(f"Training classification head for {self.epochs} epochs...")
        for epoch in range(1, self.epochs + 1):
            head.train()
            total_loss = 0.0
            for bx, by in train_loader:
                bx, by = bx.to(device), by.to(device)
                optimizer.zero_grad()
                logits = head(bx)
                loss = criterion(logits, by)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            head.eval()
            with torch.no_grad():
                val_logits = head(val_x_tensor.to(device))
                val_loss = criterion(val_logits, val_y_tensor.to(device)).item()
                val_preds = torch.argmax(val_logits, dim=-1).cpu().tolist()
                val_metrics = compute_classification_metrics(val_labels, val_preds, class_names=CLASS_NAMES)

            logger.info(
                f"[{self.exp_id}] Epoch {epoch}/{self.epochs} | Train Loss: {total_loss/len(train_loader):.4f} | "
                f"Val Loss: {val_loss:.4f} | Val F1: {val_metrics['macro_f1']:.4f}"
            )

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_state = head.state_dict().copy()

        if best_state is not None:
            head.load_state_dict(best_state)
            torch.save(best_state, os.path.join(self.exp_dir, "checkpoint.pt"))

        # Test evaluation
        head.eval()
        with torch.no_grad():
            test_logits = head(test_x_tensor.to(device))
            test_probs = F.softmax(test_logits, dim=-1).cpu().numpy()
            test_preds = np.argmax(test_probs, axis=1).tolist()

        test_metrics = compute_classification_metrics(
            test_labels,
            test_preds,
            y_prob=test_probs,
            class_names=CLASS_NAMES
        )

        # Domain breakdown
        domain_breakdown = {}
        for ds in ["liar_plus", "coaid", "fever", "indic"]:
            ds_samples = load_jsonl_samples(os.path.join(PROCESSED_DIR, ds, "test.jsonl"))
            d_texts = [s["claim_text"] for s in ds_samples if s.get("grounded_label") in LABEL_MAP]
            d_labels = [LABEL_MAP[s["grounded_label"]] for s in ds_samples if s.get("grounded_label") in LABEL_MAP]
            if d_texts:
                d_embs = encoder.encode(d_texts, batch_size=self.batch_size, show_progress_bar=False, normalize_embeddings=True)
                d_x = torch.tensor(d_embs, dtype=torch.float32).to(device)
                with torch.no_grad():
                    d_logits = head(d_x)
                    d_probs = F.softmax(d_logits, dim=-1).cpu().numpy()
                    d_preds = np.argmax(d_probs, axis=1).tolist()
                d_metrics = compute_classification_metrics(d_labels, d_preds, d_probs, class_names=CLASS_NAMES)
                domain_breakdown[ds] = {
                    "accuracy": d_metrics["accuracy"],
                    "macro_f1": d_metrics["macro_f1"]
                }

        results = {
            "experiment_id": self.exp_id,
            "encoder_model": self.model_name,
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

        config = {
            "experiment_id": self.exp_id,
            "encoder_model": self.model_name,
            "embed_dim": embed_dim,
            "batch_size": self.batch_size,
            "epochs": self.epochs,
            "lr": self.lr,
            "seed": self.seed,
            "classes": CLASS_NAMES
        }
        with open(os.path.join(self.exp_dir, "config.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        with open(os.path.join(self.exp_dir, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump({"experiment_id": self.exp_id, "status": "COMPLETED", "metrics": results}, f, indent=2)

        logger.info(
            f"[{self.exp_id}] Finished => Test Acc: {test_metrics['accuracy']}, Macro-F1: {test_metrics['macro_f1']}, ECE: {test_metrics.get('ece')}"
        )
        return results


if __name__ == "__main__":
    # 1. English transformer (all-MiniLM-L6-v2)
    logger.info("Starting English Transformer Pipeline...")
    trainer_en = TransformerTrainer(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        exp_dir=EXP03_DIR,
        exp_id="exp03_transformer_english",
        epochs=8,
        batch_size=64
    )
    trainer_en.run_training_pipeline()

    # 2. Multilingual transformer (paraphrase-multilingual-MiniLM-L12-v2)
    logger.info("Starting Multilingual Transformer Pipeline...")
    trainer_multi = TransformerTrainer(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        exp_dir=EXP04_DIR,
        exp_id="exp04_transformer_multilingual",
        epochs=8,
        batch_size=64
    )
    trainer_multi.run_training_pipeline()
