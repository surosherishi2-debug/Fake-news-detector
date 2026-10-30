"""Temporal Credibility Decay implementation for TruthLens-Omni.

Mathematical Formulation (TruthLens Section 3.3):
    w(t) = exp(-λ * Δt)
Where:
    - Δt is the temporal obsolescence distance (in years) between the claim and the evidence source.
    - λ is the learned decay constant (default = 0.1).
"""

from datetime import datetime, timezone
import math
from typing import Optional
from src.core.config import settings

def calculate_temporal_decay(
    claim_time: Optional[datetime],
    evidence_time: Optional[datetime],
    decay_lambda: Optional[float] = None,
) -> float:
    """
    Calculate the temporal credibility weight w(t) between claim and evidence.
    
    Args:
        claim_time: Timestamp of the claim being evaluated.
        evidence_time: Timestamp of the retrieved evidence document.
        decay_lambda: Decay rate parameter λ (defaults to settings.TEMPORAL_LAMBDA = 0.1).
        
    Returns:
        float: Normalized temporal credibility weight in range (0.0, 1.0].
    """
    if decay_lambda is None:
        decay_lambda = settings.TEMPORAL_LAMBDA

    # If timestamps are missing, assume neutral baseline weight
    if evidence_time is None:
        return 0.85
    
    if claim_time is None:
        claim_time = datetime.now(timezone.utc)

    # Normalize tz-aware vs naive datetimes
    if claim_time.tzinfo is not None and evidence_time.tzinfo is None:
        evidence_time = evidence_time.replace(tzinfo=claim_time.tzinfo)
    elif claim_time.tzinfo is None and evidence_time.tzinfo is not None:
        claim_time = claim_time.replace(tzinfo=evidence_time.tzinfo)

    # Calculate difference in years
    delta_seconds = (claim_time - evidence_time).total_seconds()
    
    # If evidence was published AFTER or simultaneously with the claim,
    # it is a contemporary or retroactive fact-check -> maximal weight
    if delta_seconds <= 0:
        return 1.0

    delta_years = delta_seconds / (365.25 * 86400.0)
    
    # Exponential decay: w(t) = exp(-λ * Δt)
    weight = math.exp(-decay_lambda * delta_years)
    
    # Bound strictly between [0.01, 1.0] to prevent arithmetic underflow
    return max(0.01, min(1.0, weight))
