"""NLP package initialization."""

from src.nlp.temporal_decay import calculate_temporal_decay
from src.nlp.claim_decomposer import ClaimDecomposer

__all__ = ["calculate_temporal_decay", "ClaimDecomposer"]
