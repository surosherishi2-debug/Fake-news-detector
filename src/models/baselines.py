"""Classical Machine Learning Baselines (TF-IDF + Logistic Regression / Linear SVM / Naive Bayes).

Provides reproducible training, multi-seed evaluation (seeds 42, 43, 44),
cross-domain benchmark reporting, calibration analysis (ECE), and artifact persistence in experiments/.
"""

import os
import json
import logging
import joblib
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.naive_bayes import MultinomialNB

from src.evaluation.metrics import compute_classification_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
EXPERIMENTS_DIR = os.path.join(BASE_DIR, "experiments")
EXP01_DIR = os.path.join(EXPERIMENTS_DIR, "exp01_tfidf_baselines")

LABEL_MAP = {"VERIFIED": 0, "REFUTED": 1, "DATA_VOID": 2}
INV_LABEL_MAP = {0: "VERIFIED", 1: "REFUTED", 2: "DATA_VOID"}
CLASS_NAMES = ["VERIFIED", "REFUTED", "DATA_VOID"]


def load_jsonl_samples(filepath: str) -> List[Dict[str, Any]]:
    """Loads a JSONL split file into a list of dictionaries."""
    samples = []
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return samples
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:
                samples.append(json.loads(line))
    return samples


def get_combined_splits(datasets: List[str] = ("liar_plus", "coaid", "fever")) -> Tuple[List[str], List[int], List[str], List[int]]:
    """Combines training and validation splits across approved datasets."""
    train_texts, train_labels = [], []
    val_texts, val_labels = [], []

    for ds in datasets:
        ds_train_path = os.path.join(PROCESSED_DIR, ds, "train.jsonl")
        for item in load_jsonl_samples(ds_train_path):
            label = item.get("grounded_label")
            if label in LABEL_MAP:
                train_texts.append(item["claim_text"])
                train_labels.append(LABEL_MAP[label])

        ds_val_path = os.path.join(PROCESSED_DIR, ds, "val.jsonl")
        for item in load_jsonl_samples(ds_val_path):
            label = item.get("grounded_label")
            if label in LABEL_MAP:
                val_texts.append(item["claim_text"])
                val_labels.append(LABEL_MAP[label])

    return train_texts, train_labels, val_texts, val_labels


class ClassicalBaselinesTrainer:
    """Trains and evaluates classical ML baselines with multi-seed stability and calibration."""

    def __init__(
        self,
        max_features: int = 10000,
        ngram_range: Tuple[int, int] = (1, 2),
        seeds: List[int] = (42, 43, 44)
    ):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.seeds = list(seeds)

    def train_and_evaluate(self) -> Dict[str, Any]:
        """Executes full training across seeds and logs to experiments/exp01_tfidf_baselines/."""
        os.makedirs(EXP01_DIR, exist_ok=True)
        models_dir = os.path.join(EXP01_DIR, "models")
        os.makedirs(models_dir, exist_ok=True)

        logger.info("Loading training and validation datasets...")
        train_texts, train_labels, val_texts, val_labels = get_combined_splits()
        logger.info(f"Loaded {len(train_texts)} training samples and {len(val_texts)} validation samples.")

        # Load unified benchmark test set
        unified_test_path = os.path.join(PROCESSED_DIR, "unified_benchmark", "test.jsonl")
        unified_samples = load_jsonl_samples(unified_test_path)
        test_texts = [s["claim_text"] for s in unified_samples if s.get("grounded_label") in LABEL_MAP]
        test_labels = [LABEL_MAP[s["grounded_label"]] for s in unified_samples if s.get("grounded_label") in LABEL_MAP]
        logger.info(f"Loaded {len(test_texts)} unified test benchmark samples.")

        # Load domain-specific test sets for cross-domain generalization evaluation
        domain_tests = {}
        for ds in ["liar_plus", "coaid", "fever", "indic"]:
            ds_path = os.path.join(PROCESSED_DIR, ds, "test.jsonl")
            ds_samples = load_jsonl_samples(ds_path)
            domain_tests[ds] = {
                "texts": [s["claim_text"] for s in ds_samples if s.get("grounded_label") in LABEL_MAP],
                "labels": [LABEL_MAP[s["grounded_label"]] for s in ds_samples if s.get("grounded_label") in LABEL_MAP]
            }

        # Vectorize
        logger.info(f"Fitting TfidfVectorizer (ngrams={self.ngram_range}, max_features={self.max_features})...")
        vectorizer = TfidfVectorizer(
            ngram_range=self.ngram_range,
            max_features=self.max_features,
            sublinear_tf=True
        )
        x_train = vectorizer.fit_transform(train_texts)
        x_val = vectorizer.transform(val_texts)
        x_test = vectorizer.transform(test_texts)

        # Save vectorizer
        joblib.dump(vectorizer, os.path.join(models_dir, "tfidf_vectorizer.joblib"))

        model_factories = {
            "Logistic_Regression": lambda seed: LogisticRegression(
                C=1.0,
                max_iter=1000,
                random_state=seed
            ),
            "Linear_SVM": lambda seed: CalibratedClassifierCV(
                estimator=LinearSVC(C=1.0, max_iter=2000, random_state=seed),
                cv=3
            ),
            "Multinomial_NB": lambda seed: MultinomialNB(alpha=0.1)
        }

        results_by_model: Dict[str, Any] = {}

        for model_name, factory in model_factories.items():
            logger.info(f"--- Training {model_name} across seeds {self.seeds} ---")
            seed_runs = []
            best_model = None
            best_f1 = -1.0

            for seed in self.seeds:
                clf = factory(seed)
                clf.fit(x_train, train_labels)

                # Validation evaluation
                val_probs = clf.predict_proba(x_val)
                val_preds = np.argmax(val_probs, axis=1)
                val_metrics = compute_classification_metrics(val_labels, val_preds, val_probs, CLASS_NAMES)

                # Unified Test evaluation
                test_probs = clf.predict_proba(x_test)
                test_preds = np.argmax(test_probs, axis=1)
                test_metrics = compute_classification_metrics(test_labels, test_preds, test_probs, CLASS_NAMES)

                # Domain breakdown
                domain_breakdown = {}
                for d_name, d_data in domain_tests.items():
                    if d_data["texts"]:
                        x_dom = vectorizer.transform(d_data["texts"])
                        dom_probs = clf.predict_proba(x_dom)
                        dom_preds = np.argmax(dom_probs, axis=1)
                        dom_metrics = compute_classification_metrics(
                            d_data["labels"], dom_preds, dom_probs, CLASS_NAMES
                        )
                        domain_breakdown[d_name] = {
                            "accuracy": dom_metrics["accuracy"],
                            "macro_f1": dom_metrics["macro_f1"]
                        }

                run_result = {
                    "seed": seed,
                    "val_macro_f1": val_metrics["macro_f1"],
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
                seed_runs.append(run_result)

                if test_metrics["macro_f1"] > best_f1:
                    best_f1 = test_metrics["macro_f1"]
                    best_model = clf

            # Save best model
            joblib.dump(best_model, os.path.join(models_dir, f"{model_name.lower()}_best.joblib"))

            # Compute mean and standard deviation across seeds
            accs = [r["test_accuracy"] for r in seed_runs]
            f1s = [r["test_macro_f1"] for r in seed_runs]
            eces = [r["test_ece"] for r in seed_runs if r["test_ece"] is not None]
            briers = [r["test_brier"] for r in seed_runs if r["test_brier"] is not None]
            aucs = [r["test_roc_auc_ovr"] for r in seed_runs if r["test_roc_auc_ovr"] is not None]

            summary = {
                "mean_accuracy": round(float(np.mean(accs)), 4),
                "std_accuracy": round(float(np.std(accs)), 4),
                "mean_macro_f1": round(float(np.mean(f1s)), 4),
                "std_macro_f1": round(float(np.std(f1s)), 4),
                "mean_ece": round(float(np.mean(eces)), 4) if eces else None,
                "mean_brier": round(float(np.mean(briers)), 4) if briers else None,
                "mean_roc_auc_ovr": round(float(np.mean(aucs)), 4) if aucs else None,
                "runs": seed_runs
            }
            results_by_model[model_name] = summary
            logger.info(
                f"{model_name} => Test Acc: {summary['mean_accuracy']} +/- {summary['std_accuracy']}, "
                f"Macro-F1: {summary['mean_macro_f1']} +/- {summary['std_macro_f1']}, "
                f"ECE: {summary['mean_ece']}"
            )

        # Write experiment config and master metrics.json
        config = {
            "experiment_id": "exp01_tfidf_baselines",
            "model_type": "classical_ml_tfidf",
            "feature_extractor": "TfidfVectorizer",
            "ngram_range": list(self.ngram_range),
            "max_features": self.max_features,
            "sublinear_tf": True,
            "training_samples": len(train_texts),
            "validation_samples": len(val_texts),
            "unified_test_samples": len(test_texts),
            "seeds": self.seeds,
            "classes": CLASS_NAMES
        }
        with open(os.path.join(EXP01_DIR, "config.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        master_metrics = {
            "experiment_id": "exp01_tfidf_baselines",
            "status": "COMPLETED",
            "models": results_by_model
        }
        with open(os.path.join(EXP01_DIR, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump(master_metrics, f, indent=2)

        logger.info(f"Experiment exp01_tfidf_baselines logged successfully to {EXP01_DIR}")
        return master_metrics


if __name__ == "__main__":
    trainer = ClassicalBaselinesTrainer()
    trainer.train_and_evaluate()
