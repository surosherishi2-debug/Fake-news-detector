"""Unit tests for CEAM PyTorch architecture, benchmark datasets, adversarial attacks, and RSS ingestion."""

import pytest
import torch
from src.models.ceam_model import CEAMTruthLensModel, CrossAttentionLayer, MultimodalGatedFusion
from src.models.adversarial_tester import AdversarialAttackSimulator
from src.models.evaluator import ModelEvaluator
from src.data.dataset_loader import DatasetLoader
from src.data.rss_crawler import RSSNewsCrawler
from src.data.news_database import EpistemicDatabase

def test_dataset_loader_benchmarks():
    loader = DatasetLoader()
    pune_samples = loader.get_dataset("pune_fakenews_2024")
    assert len(pune_samples) >= 8
    
    # Verify multilingual support in PuneFakeNews-2024
    languages = set(s.language for s in pune_samples)
    assert "en" in languages
    assert "mr" in languages  # Marathi regional Indic language

    liar_samples = loader.get_dataset("liar_plus")
    assert len(liar_samples) >= 4

    metrics = loader.compute_dataset_metrics("pune_fakenews_2024")
    assert metrics.total_samples == len(pune_samples)
    assert "FAKE" in metrics.class_distribution
    assert "REAL" in metrics.class_distribution

def test_ceam_model_forward():
    model = CEAMTruthLensModel(vocab_size=1000, embed_dim=64, graph_dim=32, num_classes=4, num_heads=4)
    model.eval()

    batch_size = 2
    claim_ids = torch.randint(1, 999, (batch_size, 10))
    evidence_ids = torch.randint(1, 999, (batch_size, 25))
    graph_emb = torch.randn(batch_size, 32)
    temporal_weights = torch.tensor([[0.85], [0.35]])

    logits, attn = model(claim_ids, evidence_ids, graph_emb, temporal_decay_weights=temporal_weights)

    assert logits.shape == (batch_size, 4)
    assert attn.shape == (batch_size, 4, 10, 25)

    # Test predict helper
    pred = model.predict_epistemic_state(claim_ids[:1], evidence_ids[:1], graph_emb[:1], temporal_weights[:1])
    assert "verdict" in pred
    assert pred["verdict"] in ["REAL", "FAKE", "SATIRE", "DATA_VOID"]
    assert "probabilities" in pred
    assert len(pred["probabilities"]) == 4

def test_adversarial_synonym_perturbation():
    adv = AdversarialAttackSimulator()
    original = "The FDA confirmed the approved vaccine is safe and proven effective in clinical trials."
    perturbed, subs, mod_rate = adv.perturb_text(original, perturbation_budget=0.40)

    assert len(subs) > 0
    assert mod_rate > 0.0
    assert original != perturbed
    # Verify substitution recorded
    for sub in subs:
        assert sub["original"].lower() in adv.synonym_map
        assert sub["replacement"] in adv.synonym_map[sub["original"].lower()]

def test_model_evaluator_suite():
    evaluator = ModelEvaluator()
    report = evaluator.run_benchmark_suite("pune_fakenews_2024")
    assert report.dataset_evaluated == "pune_fakenews_2024"
    assert len(report.models) >= 4
    
    # Check that TruthLens outperforms baselines on adversarial retention
    truthlens_row = next(m for m in report.models if "TruthLens" in m.model_name)
    bert_row = next(m for m in report.models if "BERT-Base" in m.model_name)
    
    assert truthlens_row.accuracy > bert_row.accuracy
    assert truthlens_row.robustness_retention > bert_row.robustness_retention

def test_rss_crawler_offline_fallback():
    crawler = RSSNewsCrawler()
    result = crawler.sync_feeds(force_live=False)
    assert result.success is True
    assert result.articles_ingested >= 3
    assert result.claims_extracted >= 3
    assert result.mode == "OFFLINE_ARCHIVE_FALLBACK"
