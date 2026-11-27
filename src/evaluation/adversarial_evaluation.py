"""Adversarial Attack Evaluation Suite (TextFooler / DeepWordBug Stress Testing).

Measures empirical robustness under adversarial semantic perturbation:
- Clean Test F1
- Adversarial Test F1 (under 20% synonym substitution / character typo budget)
- Robustness Retention Ratio R = (F1_adv / F1_clean) * 100%

Addresses failure mode 1: Surface token over-indexing and lexical susceptibility.
"""

import os
import json
import logging
import joblib
import numpy as np
from typing import Dict, Any, List

import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

from src.models.adversarial_tester import AdversarialAttackSimulator
from src.evaluation.metrics import compute_classification_metrics
from src.models.baselines import (
    load_jsonl_samples,
    LABEL_MAP,
    CLASS_NAMES,
    PROCESSED_DIR
)
from src.models.transformer_models import TransformerClassifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXPERIMENTS_DIR = os.path.join(BASE_DIR, "experiments")


class AdversarialBenchmarkRunner:
    """Evaluates trained models on clean vs adversarially perturbed test samples."""

    def __init__(self, sample_limit: int = 500, perturbation_budget: float = 0.20):
        self.sample_limit = sample_limit
        self.perturbation_budget = perturbation_budget
        self.simulator = AdversarialAttackSimulator()

    def run_benchmark(self) -> Dict[str, Any]:
        logger.info(f"Generating adversarial test set (N={self.sample_limit}, budget={self.perturbation_budget})...")
        test_path = os.path.join(PROCESSED_DIR, "unified_benchmark", "test.jsonl")
        samples = load_jsonl_samples(test_path)[:self.sample_limit]

        clean_texts = [s["claim_text"] for s in samples if s.get("grounded_label") in LABEL_MAP]
        clean_labels = [LABEL_MAP[s["grounded_label"]] for s in samples if s.get("grounded_label") in LABEL_MAP]

        # Generate perturbed texts
        adv_texts = []
        for text in clean_texts:
            perturbed, _, _ = self.simulator.perturb_text(
                text,
                perturbation_budget=self.perturbation_budget,
                attack_type="textfooler"
            )
            adv_texts.append(perturbed)

        results = {}

        # 1. Evaluate TF-IDF + Logistic Regression
        lr_model_path = os.path.join(EXPERIMENTS_DIR, "exp01_tfidf_baselines", "models", "logistic_regression_best.joblib")
        vec_path = os.path.join(EXPERIMENTS_DIR, "exp01_tfidf_baselines", "models", "tfidf_vectorizer.joblib")
        if os.path.exists(lr_model_path) and os.path.exists(vec_path):
            logger.info("Evaluating TF-IDF + Logistic Regression under adversarial perturbation...")
            vec = joblib.load(vec_path)
            clf = joblib.load(lr_model_path)

            x_clean = vec.transform(clean_texts)
            x_adv = vec.transform(adv_texts)

            clean_preds = clf.predict(x_clean)
            adv_preds = clf.predict(x_adv)

            m_clean = compute_classification_metrics(clean_labels, clean_preds, class_names=CLASS_NAMES)
            m_adv = compute_classification_metrics(clean_labels, adv_preds, class_names=CLASS_NAMES)

            retention = round((m_adv["macro_f1"] / max(1e-4, m_clean["macro_f1"])) * 100, 2)
            results["Logistic_Regression"] = {
                "clean_f1": m_clean["macro_f1"],
                "adversarial_f1": m_adv["macro_f1"],
                "robustness_retention": retention,
                "clean_acc": m_clean["accuracy"],
                "adversarial_acc": m_adv["accuracy"]
            }

        # 2. Evaluate English Transformer (all-MiniLM-L6-v2)
        transformer_ckpt = os.path.join(EXPERIMENTS_DIR, "exp03_transformer_english", "checkpoint.pt")
        if os.path.exists(transformer_ckpt):
            logger.info("Evaluating Pre-trained Transformer (all-MiniLM-L6-v2) under adversarial perturbation...")
            encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            head = TransformerClassifier(embed_dim=384, hidden_dim=128, num_classes=3, dropout=0.2)
            head.load_state_dict(torch.load(transformer_ckpt, map_location="cpu"))
            head.eval()

            embs_clean = encoder.encode(clean_texts, batch_size=64, show_progress_bar=False, normalize_embeddings=True)
            embs_adv = encoder.encode(adv_texts, batch_size=64, show_progress_bar=False, normalize_embeddings=True)

            with torch.no_grad():
                logits_clean = head(torch.tensor(embs_clean, dtype=torch.float32))
                logits_adv = head(torch.tensor(embs_adv, dtype=torch.float32))

            preds_clean = torch.argmax(logits_clean, dim=-1).tolist()
            preds_adv = torch.argmax(logits_adv, dim=-1).tolist()

            m_clean = compute_classification_metrics(clean_labels, preds_clean, class_names=CLASS_NAMES)
            m_adv = compute_classification_metrics(clean_labels, preds_adv, class_names=CLASS_NAMES)

            retention = round((m_adv["macro_f1"] / max(1e-4, m_clean["macro_f1"])) * 100, 2)
            results["Transformer_English_MiniLM"] = {
                "clean_f1": m_clean["macro_f1"],
                "adversarial_f1": m_adv["macro_f1"],
                "robustness_retention": retention,
                "clean_acc": m_clean["accuracy"],
                "adversarial_acc": m_adv["accuracy"]
            }

        # Save adversarial evaluation metrics
        out_path = os.path.join(EXPERIMENTS_DIR, "adversarial_metrics.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Adversarial evaluation saved to {out_path}: {results}")
        return results


if __name__ == "__main__":
    runner = AdversarialBenchmarkRunner(sample_limit=500, perturbation_budget=0.20)
    runner.run_benchmark()
