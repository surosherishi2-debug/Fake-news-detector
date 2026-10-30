"""Unit tests for Neuro-Symbolic TruthLensEngine and FastAPI Server."""

from src.core.types import VerificationRequest, VerificationVerdict, HighlightStatus
from src.fusion.truthlens_engine import TruthLensEngine
from src.api.server import (
    health_check,
    get_domain_trust,
    verify_article,
    scrape_article_url,
    score_community_notes,
    get_sample_cascade,
    ScrapeRequest,
    ConsensusRequest,
)
from src.graph.consensus_matrix import NoteRating

def test_truthlens_engine_fake_claim_with_nutrition_card():
    engine = TruthLensEngine()
    req = VerificationRequest(
        text="Viral claim: COVID-19 vaccines contain microchips designed for human tracking.",
        publisher="dailyconspiracy.net",
    )
    result = engine.verify(req)
    assert result.verdict == VerificationVerdict.FAKE
    assert result.confidence_score >= 0.50
    assert len(result.claims) >= 1
    assert result.nutrition_card is not None
    assert result.nutrition_card.factual_grounding_score <= 50.0
    assert result.claims[0].highlight_status == HighlightStatus.REFUTED
    assert "Reuters" in result.claims[0].citation or "WHO" in result.claims[0].citation

def test_truthlens_engine_satire_disentanglement():
    engine = TruthLensEngine()
    req = VerificationRequest(
        text="NASA Announces Plans To Colonize Sun At Night To Avoid Burning Up.",
        publisher="theonion.com",
    )
    result = engine.verify(req)
    assert "Satirical Parody" in result.explanation
    assert result.nutrition_card is not None

def test_truthlens_engine_zero_assumption_data_void():
    """System must strictly refuse to guess when zero accredited evidence exists."""
    engine = TruthLensEngine()
    req = VerificationRequest(
        text="Unconfirmed rumor claims local municipal office closed early on Tuesday.",
        publisher="unregistered-unknown-source.xyz",
    )
    result = engine.verify(req)
    assert result.verdict == VerificationVerdict.UNCERTAIN
    assert "Data-Void" in result.explanation

def test_api_endpoints():
    # 1. Health check
    res_health = health_check()
    assert res_health["status"] == "healthy"

    # 2. Domain trust check
    res_trust = get_domain_trust("reuters.com")
    assert res_trust["trust_score"] >= 0.90
    assert res_trust["category"] == "verified"

    # 3. Verification endpoint
    res_verify = verify_article(
        VerificationRequest(
            text="Scientists at ISRO confirmed lunar water and mineral ice near the south pole.",
            publisher="pib.gov.in",
        )
    )
    assert res_verify.verdict is not None
    assert res_verify.confidence_score > 0
    assert len(res_verify.provenance_chain) >= 1
    assert res_verify.nutrition_card is not None

    # 4. Sample cascade endpoint
    cascade = get_sample_cascade()
    assert cascade.article_id is not None
    assert len(cascade.nodes) >= 5
    assert len(cascade.edges) >= 4

    # 5. Consensus score endpoint
    consensus_res = score_community_notes(
        ConsensusRequest(
            ratings=[
                NoteRating(rater_id="u1", note_id="n1", rating=1.0),
                NoteRating(rater_id="u2", note_id="n1", rating=1.0),
                NoteRating(rater_id="u3", note_id="n1", rating=1.0),
            ]
        )
    )
    assert "n1" in consensus_res

    # 6. Scrape endpoint
    scrape_res = scrape_article_url(ScrapeRequest(url="http://invalid-nonexistent-domain-test.com"))
    assert scrape_res.status == "failed"
