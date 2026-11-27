"""Unit and integration tests for Phase 4: Retrieval, Explainability, and Calibrated Abstention."""

import pytest
from datetime import datetime, timezone

from src.retrieval.knowledge_store import KnowledgeStore
from src.retrieval.evidence_retriever import TwoStageEvidenceRetriever
from src.nlp.explainer import TruthLensExplainer
from src.fusion.truthlens_engine import TruthLensEngine
from src.core.types import VerificationRequest, VerificationVerdict, HighlightStatus


def test_knowledge_store_initialization():
    store = KnowledgeStore()
    docs = store.get_corpus()
    embs = store.get_embeddings()
    assert len(docs) >= 10, "Expected at least 10 seeded evidence records"
    assert embs is not None
    assert embs.shape[0] == len(docs)
    assert embs.shape[1] == 384  # MiniLM embedding dimension


def test_dense_retrieval_covid_conspiracy():
    retriever = TwoStageEvidenceRetriever()
    query = "COVID vaccines contain secret microchips and alter human reproductive organs."
    evs, meta = retriever.retrieve_and_rerank(query)

    assert meta["is_evidence_void"] is False
    assert meta["max_dense_similarity"] >= 0.60
    assert meta["suggested_grounded_verdict"] == "REFUTED"
    assert len(evs) >= 1
    assert "microchip" in evs[0].snippet.lower() or "microchip" in evs[0].source_title.lower()


def test_dense_retrieval_calibrated_abstention():
    retriever = TwoStageEvidenceRetriever(abstention_threshold=0.42)
    # Completely ungrounded random assertion
    query = "The local grocery store manager owns three purple bicycles in the basement."
    evs, meta = retriever.retrieve_and_rerank(query)

    assert meta["is_evidence_void"] is True
    assert meta["max_dense_similarity"] < 0.42
    assert meta["suggested_grounded_verdict"] == "DATA_VOID"


def test_dense_retrieval_indic_marathi():
    retriever = TwoStageEvidenceRetriever()
    query = "पुण्यात लष्कर तैनात करून संपूर्ण संचारबंदी लागू केल्याचा दावा खोटा आहे."
    evs, meta = retriever.retrieve_and_rerank(query)

    assert meta["is_indic"] is True
    assert meta["is_evidence_void"] is False
    assert meta["max_dense_similarity"] >= retriever.abstention_threshold
    assert len(evs) >= 1
    assert "पुणे" in evs[0].source_title or "पुणे" in evs[0].snippet


def test_explainer_token_attribution_and_trail():
    retriever = TwoStageEvidenceRetriever()
    explainer = TruthLensExplainer()

    query = "Official FDA report confirmed the vaccine is safe and effective in clinical trials."
    evs, meta = retriever.retrieve_and_rerank(query)
    explanation = explainer.explain(query, evs, meta, is_satirical_source=False)

    assert explanation.verdict == "VERIFIED"
    assert explanation.confidence > 0.60
    assert explanation.is_abstained is False
    assert len(explanation.token_attributions) > 0
    assert len(explanation.evidence_trail) > 0
    assert explanation.nutrition_card.factual_grounding_score >= 0.0


def test_explainer_abstention_explanation():
    retriever = TwoStageEvidenceRetriever(abstention_threshold=0.42)
    explainer = TruthLensExplainer()

    query = "Unknown individual allegedly found an unusual green gemstone in their teacup."
    evs, meta = retriever.retrieve_and_rerank(query)
    explanation = explainer.explain(query, evs, meta, is_satirical_source=False)

    assert explanation.verdict == "DATA_VOID"
    assert explanation.confidence == 0.0
    assert explanation.is_abstained is True
    assert "abstains from asserting truth or falsehood" in explanation.plain_language_summary


def test_truthlens_engine_full_integration():
    engine = TruthLensEngine()
    req = VerificationRequest(
        text="Viral posts claim COVID-19 vaccines contain secret microchips designed for human tracking.",
        publisher="dailyconspiracy.net"
    )
    result = engine.verify(req)

    assert result.verdict == VerificationVerdict.FAKE
    assert result.confidence_score >= 0.80
    assert result.latency_ms > 0
    assert any(c.highlight_status == HighlightStatus.REFUTED for c in result.claims)
