"""Unit tests for Claim Decomposer."""

from src.nlp.claim_decomposer import ClaimDecomposer

def test_decomposer_factual_assertions():
    decomposer = ClaimDecomposer()
    text = (
        "The World Health Organization confirmed that over 10 million vaccine doses "
        "were administered in March 2023. Scientists reported a 15 percent drop in cases."
    )
    claims = decomposer.decompose(text)
    assert len(claims) >= 1
    assert any(c.domain == "health" for c in claims)
    assert any("World Health Organization" in c.entities or "March" in c.text for c in claims)
    for c in claims:
        assert c.check_worthiness >= 0.50

def test_decomposer_filters_opinions():
    decomposer = ClaimDecomposer()
    text = "In my opinion, perhaps we should go to the cinema tomorrow. Hello and welcome everyone!"
    claims = decomposer.decompose(text)
    # Pure opinion with no facts should either be filtered or have low check-worthiness
    if claims:
        assert claims[0].check_worthiness <= 0.65

def test_decomposer_empty_input():
    decomposer = ClaimDecomposer()
    assert decomposer.decompose("") == []
    assert decomposer.decompose("   ") == []
