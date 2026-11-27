"""Unit tests for the evaluation metrics engine (Accuracy, F1, ECE, Brier, ROC-AUC)."""

import numpy as np
import pytest
from src.evaluation.metrics import (
    compute_ece,
    compute_multi_brier_score,
    compute_classification_metrics
)

def test_compute_ece_perfect_calibration():
    # Model that predicts probability 1.0 and is always right
    y_true = np.array([0, 1, 0, 1, 2])
    y_prob = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ])
    ece, bins = compute_ece(y_true, y_prob, n_bins=10)
    assert ece == 0.0
    assert len(bins) == 10

def test_compute_ece_uncalibrated():
    # Model that is 100% confident but always wrong
    y_true = np.array([0, 0, 0, 0])
    y_prob = np.array([
        [0.0, 1.0],
        [0.0, 1.0],
        [0.0, 1.0],
        [0.0, 1.0]
    ])
    ece, bins = compute_ece(y_true, y_prob, n_bins=10)
    # accuracy is 0.0, confidence is 1.0, so ece should be 1.0
    assert pytest.approx(ece, 0.01) == 1.0

def test_compute_brier_score():
    y_true = np.array([0, 1])
    # Perfect predictions
    y_prob_perfect = np.array([[1.0, 0.0], [0.0, 1.0]])
    assert compute_multi_brier_score(y_true, y_prob_perfect, num_classes=2) == 0.0

    # Half confident predictions
    y_prob_half = np.array([[0.5, 0.5], [0.5, 0.5]])
    # (0.5^2 + 0.5^2) = 0.5
    assert pytest.approx(compute_multi_brier_score(y_true, y_prob_half, num_classes=2), 0.01) == 0.5

def test_classification_metrics_multiclass():
    y_true = [0, 1, 2, 0, 1, 2]
    y_pred = [0, 1, 1, 0, 1, 2]
    y_prob = np.array([
        [0.8, 0.1, 0.1],
        [0.1, 0.8, 0.1],
        [0.1, 0.7, 0.2],  # wrong
        [0.9, 0.05, 0.05],
        [0.2, 0.7, 0.1],
        [0.1, 0.2, 0.7]
    ])
    class_names = ["VERIFIED", "REFUTED", "DATA_VOID"]
    metrics = compute_classification_metrics(y_true, y_pred, y_prob=y_prob, class_names=class_names)

    assert metrics["sample_count"] == 6
    assert metrics["accuracy"] == pytest.approx(5 / 6, 0.01)
    assert "macro_f1" in metrics
    assert "ece" in metrics
    assert "brier_score" in metrics
    assert "roc_auc_ovr" in metrics
    assert "confusion_matrix" in metrics
    assert "VERIFIED" in metrics["per_class"]
