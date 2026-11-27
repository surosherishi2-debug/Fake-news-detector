"""Unit and regression tests for Phase 3 Model Ladder & Evaluation components."""

import os
import pytest
import torch
import numpy as np
import joblib

from src.models.ceam_model import CEAMTruthLensModel
from src.models.deep_models import BiLSTMClassifier, TokenVocab
from src.models.transformer_models import TransformerClassifier
from src.evaluation.metrics import compute_classification_metrics, compute_ece
from src.evaluation.generate_results_table import generate_results_table
from src.models.adversarial_tester import AdversarialAttackSimulator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(BASE_DIR, "experiments")


def test_classical_baseline_artifacts_exist():
    vec_path = os.path.join(EXPERIMENTS_DIR, "exp01_tfidf_baselines", "models", "tfidf_vectorizer.joblib")
    model_path = os.path.join(EXPERIMENTS_DIR, "exp01_tfidf_baselines", "models", "logistic_regression_best.joblib")
    assert os.path.exists(vec_path), "TF-IDF vectorizer artifact missing"
    assert os.path.exists(model_path), "Logistic Regression model artifact missing"

    vec = joblib.load(vec_path)
    clf = joblib.load(model_path)
    sample_text = ["The CDC officially authorized the new vaccine booster formulation."]
    x = vec.transform(sample_text)
    probs = clf.predict_proba(x)
    assert probs.shape == (1, 3)
    assert pytest.approx(float(np.sum(probs)), 0.01) == 1.0


def test_bilstm_architecture_forward():
    vocab_size = 500
    batch_size = 4
    seq_len = 32
    model = BiLSTMClassifier(vocab_size=vocab_size, embed_dim=64, hidden_dim=64, num_classes=3)
    model.eval()

    dummy_input = torch.randint(0, vocab_size, (batch_size, seq_len))
    with torch.no_grad():
        logits = model(dummy_input)

    assert logits.shape == (batch_size, 3)


def test_transformer_classifier_head():
    head = TransformerClassifier(embed_dim=384, hidden_dim=64, num_classes=3)
    head.eval()
    dummy_emb = torch.randn(2, 384)
    with torch.no_grad():
        logits = head(dummy_emb)
    assert logits.shape == (2, 3)


def test_ceam_temporal_weight_effect():
    vocab_size = 200
    model = CEAMTruthLensModel(vocab_size=vocab_size, embed_dim=32, graph_dim=16, num_classes=3, num_heads=2)
    model.eval()

    c_ids = torch.randint(1, vocab_size, (2, 10))
    e_ids = torch.randint(1, vocab_size, (2, 20))
    g_emb = torch.randn(2, 16)

    # Compare forward with temporal decay 0.1 vs 1.0
    w_decay = torch.tensor([[0.1], [0.1]])
    w_neutral = torch.tensor([[1.0], [1.0]])

    with torch.no_grad():
        logits_decay, attn_decay = model(c_ids, e_ids, g_emb, temporal_decay_weights=w_decay)
        logits_neutral, attn_neutral = model(c_ids, e_ids, g_emb, temporal_decay_weights=w_neutral)

    assert logits_decay.shape == (2, 3)
    assert logits_neutral.shape == (2, 3)
    # The attention weights should differ due to temporal decay attenuation
    assert not torch.allclose(attn_decay, attn_neutral, atol=1e-4)


def test_master_results_table_generation():
    content = generate_results_table()
    assert len(content) > 100
    assert "TruthLens-Omni Master Benchmark Results" in content
    assert "experiments/" in content
    assert "Unified Benchmark Evaluation" in content


def test_adversarial_simulator_semantic_preservation():
    adv = AdversarialAttackSimulator()
    claim = "The approved therapy demonstrated unprecedented results in clinical trials."
    perturbed, subs, mod_rate = adv.perturb_text(claim, perturbation_budget=0.25)
    assert len(perturbed) > 0
    assert 0.0 < mod_rate <= 0.50
