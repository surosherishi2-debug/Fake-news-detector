"""Unit tests for Fact Check Client."""

from datetime import datetime, timezone
from src.retrieval.fact_check_client import FactCheckClient

def test_fact_check_offline_search():
    client = FactCheckClient()
    query = "COVID vaccine causes microchip infertility"
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    evidences = client.search_evidence(query, claim_time=now, max_results=3)

    assert len(evidences) >= 1
    top = evidences[0]
    assert "Vaccine" in top.source_title or "COVID" in top.source_title
    assert top.semantic_similarity > 0.50
    assert 0.0 < top.temporal_weight <= 1.0
    assert "False" in top.snippet

def test_fact_check_no_match():
    client = FactCheckClient()
    query = "Random unrecorded query xyz123999 nonexistent topic"
    evidences = client.search_evidence(query, max_results=3)
    assert isinstance(evidences, list)
