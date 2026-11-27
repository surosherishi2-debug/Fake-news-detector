"""Comprehensive Evaluation Metrics Engine for TruthLens-Omni.

Provides standardized, mathematically rigorous implementations of:
- Accuracy, Precision, Recall, Macro-F1, Weighted-F1
- Multi-class One-vs-Rest ROC-AUC
- Expected Calibration Error (ECE) and Reliability Diagram data
- Brier Score
- Adversarial Robustness Metrics (Clean F1, Adv F1, Robustness Retention)
"""

from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)


def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Computes Expected Calibration Error (ECE) and reliability bin statistics.

    ECE = sum_{b=1}^B (|B_b| / N) * |acc(B_b) - conf(B_b)|

    Args:
        y_true: Ground truth integer class indices, shape [N]
        y_prob: Predicted probability distribution, shape [N, C]
        n_bins: Number of confidence bins (default: 10)

    Returns:
        Tuple of:
          - ece: Float in [0.0, 1.0]
          - bin_data: List of dicts with bin-level stats (acc, conf, count, edge_low, edge_high)
    """
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)

    if len(y_prob.shape) == 1:
        # Binary case
        y_prob = np.stack([1.0 - y_prob, y_prob], axis=1)

    confidences = np.max(y_prob, axis=1)
    predictions = np.argmax(y_prob, axis=1)
    accuracies = (predictions == y_true).astype(float)

    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n_samples = len(y_true)
    bin_stats = []

    for i in range(n_bins):
        low, high = bin_boundaries[i], bin_boundaries[i + 1]
        if i == n_bins - 1:
            in_bin = (confidences >= low) & (confidences <= high)
        else:
            in_bin = (confidences >= low) & (confidences < high)

        bin_count = int(np.sum(in_bin))
        if bin_count > 0:
            bin_acc = float(np.mean(accuracies[in_bin]))
            bin_conf = float(np.mean(confidences[in_bin]))
            bin_weight = bin_count / n_samples
            ece += bin_weight * abs(bin_acc - bin_conf)
        else:
            bin_acc = 0.0
            bin_conf = float((low + high) / 2.0)

        bin_stats.append(
            {
                "bin_idx": i,
                "range": [round(float(low), 3), round(float(high), 3)],
                "count": bin_count,
                "accuracy": round(bin_acc, 4),
                "confidence": round(bin_conf, 4),
            }
        )

    return float(round(ece, 4)), bin_stats


def compute_multi_brier_score(y_true: np.ndarray, y_prob: np.ndarray, num_classes: int) -> float:
    """
    Computes multi-class Brier score:
    Brier = (1 / N) * sum_{i=1}^N sum_{c=1}^C (p_{ic} - y_{ic})^2
    """
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    n = len(y_true)
    if n == 0:
        return 0.0

    # One-hot encode ground truth
    one_hot = np.zeros((n, num_classes), dtype=float)
    for i, label in enumerate(y_true):
        if 0 <= label < num_classes:
            one_hot[i, label] = 1.0

    brier = float(np.mean(np.sum((y_prob - one_hot) ** 2, axis=1)))
    return float(round(brier, 4))


def compute_classification_metrics(
    y_true: List[int], y_pred: List[int], y_prob: np.ndarray | None = None, class_names: List[str] | None = None
) -> Dict[str, Any]:
    """
    Computes full evaluation metrics suite for truth discovery and claim verification.

    Args:
        y_true: True integer class indices
        y_pred: Predicted integer class indices
        y_prob: Optional predicted class probability matrix of shape [N, C]
        class_names: Optional label names corresponding to indices [0, 1, ..., C-1]

    Returns:
        Dictionary with accuracy, macro_f1, precision, recall, per_class_f1, roc_auc, ece, brier.
    """
    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred)
    n_samples = len(y_true_arr)

    if class_names is None:
        unique_labels = sorted(set(y_true_arr) | set(y_pred_arr))
        class_names = [f"Class_{i}" for i in unique_labels]
    else:
        unique_labels = list(range(len(class_names)))

    acc = float(accuracy_score(y_true_arr, y_pred_arr))
    prec, rec, f1, support = precision_recall_fscore_support(
        y_true_arr, y_pred_arr, labels=unique_labels, average=None, zero_division=0
    )

    macro_prec = float(np.mean(prec))
    macro_rec = float(np.mean(rec))
    macro_f1 = float(np.mean(f1))

    per_class = {}
    for idx, name in enumerate(class_names):
        if idx < len(prec):
            per_class[name] = {
                "precision": round(float(prec[idx]), 4),
                "recall": round(float(rec[idx]), 4),
                "f1": round(float(f1[idx]), 4),
                "support": int(support[idx]),
            }

    cm = confusion_matrix(y_true_arr, y_pred_arr, labels=unique_labels).tolist()

    result: Dict[str, Any] = {
        "sample_count": n_samples,
        "accuracy": round(acc, 4),
        "macro_precision": round(macro_prec, 4),
        "macro_recall": round(macro_rec, 4),
        "macro_f1": round(macro_f1, 4),
        "per_class": per_class,
        "confusion_matrix": cm,
    }

    # Probability-dependent metrics
    if y_prob is not None:
        y_prob_arr = np.asarray(y_prob)
        num_classes = len(class_names)

        # Expected Calibration Error (ECE)
        ece, bin_stats = compute_ece(y_true_arr, y_prob_arr, n_bins=10)
        result["ece"] = ece
        result["calibration_bins"] = bin_stats

        # Brier Score
        brier = compute_multi_brier_score(y_true_arr, y_prob_arr, num_classes)
        result["brier_score"] = brier

        # Multiclass ROC-AUC (OvR)
        try:
            # Check if all classes present in y_true
            present_classes = set(y_true_arr)
            if len(present_classes) > 1:
                auc = float(roc_auc_score(y_true_arr, y_prob_arr, multi_class="ovr", labels=unique_labels))
                result["roc_auc_ovr"] = round(auc, 4)
            else:
                result["roc_auc_ovr"] = None
        except Exception as e:
            result["roc_auc_ovr"] = None
            result["roc_auc_note"] = str(e)

    return result
