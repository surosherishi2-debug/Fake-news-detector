"""Unit tests for Temporal Credibility Decay module."""

import math
from datetime import datetime, timezone, timedelta
import pytest
from src.nlp.temporal_decay import calculate_temporal_decay

def test_temporal_decay_contemporary():
    """Contemporary or newer evidence must retain maximal weight w(t) = 1.0."""
    now = datetime.now(timezone.utc)
    # Evidence published on the same day as claim
    weight = calculate_temporal_decay(claim_time=now, evidence_time=now)
    assert weight == 1.0

    # Evidence published AFTER the claim (subsequent fact check)
    future_evidence = now + timedelta(days=2)
    weight_future = calculate_temporal_decay(claim_time=now, evidence_time=future_evidence)
    assert weight_future == 1.0

def test_temporal_decay_mathematical_precision():
    """Verify w(t) matches exp(-λ * Δt) for 1 year and 5 years."""
    now = datetime(2025, 1, 1, tzinfo=timezone.utc)
    one_year_prior = datetime(2024, 1, 1, tzinfo=timezone.utc)
    five_years_prior = datetime(2020, 1, 1, tzinfo=timezone.utc)

    # 1 year decay with λ = 0.1: exp(-0.1 * 1.0) ≈ 0.904837
    weight_1yr = calculate_temporal_decay(claim_time=now, evidence_time=one_year_prior, decay_lambda=0.1)
    expected_1yr = math.exp(-0.1 * (366.0 / 365.25))
    assert pytest.approx(weight_1yr, rel=1e-2) == expected_1yr

    # 5 years decay with λ = 0.1: exp(-0.1 * 5.0) ≈ 0.6065
    weight_5yr = calculate_temporal_decay(claim_time=now, evidence_time=five_years_prior, decay_lambda=0.1)
    assert 0.59 <= weight_5yr <= 0.62

def test_temporal_decay_missing_dates():
    """Graceful degradation when evidence publication date is missing."""
    now = datetime.now(timezone.utc)
    weight = calculate_temporal_decay(claim_time=now, evidence_time=None)
    assert weight == 0.85
