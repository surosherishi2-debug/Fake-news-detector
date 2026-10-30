"""Unit tests for TruthLensEngine and FastAPI Server."""

from src.core.types import VerificationRequest, VerificationVerdict
from src.fusion.truthlens_engine import TruthLensEngine
from src.api.server import app

def test_truthlens_engine_fake_claim():
    engine = TruthLensEngine()
    req = VerificationRequest(
        text="Viral claim: COVID-19 vaccines contain microchips designed for human tracking.",
        publisher="dailyconspiracy.net",
    )
    result = engine.verify(req)
    assert result.verdict == VerificationVerdict.FAKE
    assert result.confidence_score >= 0.55
    assert len(result.claims) >= 1
    assert len(result.alignments) >= 1
    assert result.latency_ms > 0

def test_api_endpoints():
    from src.api.server import health_check, get_domain_trust, verify_article

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
