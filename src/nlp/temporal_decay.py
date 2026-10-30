"""Temporal Credibility Decay implementation for TruthLens-Omni.

Mathematical Formulation (TruthLens Section 3.3):
    w(t) = exp(-λ * Δt)
Where:
    - Δt is the temporal obsolescence distance (in years) between the claim and the evidence source.
    - λ is the learned decay constant (default = 0.1).
"""

from datetime import datetime, timezone
import math
from typing import Optional, Dict
from src.core.config import settings

# Domain-specific decay rates reflecting epistemic volatility
DOMAIN_LAMBDA_MAP: Dict[str, float] = {
    "politics": 0.35,      # High turnover / fast obsolescence (~2 yr half-life)
    "election": 0.40,
    "breaking": 0.40,
    "conflict": 0.30,
    "health": 0.10,        # Public health consensus evolves moderately
    "medical": 0.10,
    "covid": 0.12,
    "climate": 0.04,
    "science": 0.01,       # Fundamental scientific discoveries persist for decades
    "astronomy": 0.01,
    "space": 0.01,
    "tech": 0.05,
    "general": 0.10,
}

def get_domain_lambda(domain_or_category: Optional[str] = None) -> float:
    """
    Retrieve domain-adaptive temporal decay parameter λ(d).
    High-volatility topics (politics) decay faster than empirical sciences.
    """
    if not domain_or_category:
        return settings.TEMPORAL_LAMBDA
    cat_lower = domain_or_category.lower().strip()
    for key, rate in DOMAIN_LAMBDA_MAP.items():
        if key in cat_lower:
            return rate
    return settings.TEMPORAL_LAMBDA

def calculate_temporal_decay(
    claim_time: Optional[datetime],
    evidence_time: Optional[datetime],
    decay_lambda: Optional[float] = None,
    domain: Optional[str] = None,
) -> float:
    """
    Calculate the temporal credibility weight w(t, d) between claim and evidence.
    
    Args:
        claim_time: Timestamp of the claim being evaluated.
        evidence_time: Timestamp of the retrieved evidence document.
        decay_lambda: Optional explicit decay rate λ. If None, derived from domain.
        domain: Domain / category string to determine adaptive decay rate.
        
    Returns:
        float: Normalized temporal credibility weight in range (0.0, 1.0].
    """
    if decay_lambda is None:
        decay_lambda = get_domain_lambda(domain)

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
