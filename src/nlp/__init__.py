"""NLP package initialization."""

from src.nlp.claim_decomposer import ClaimDecomposer
from src.nlp.preflight_auditor import PreflightAuditor, PreflightAuditReport
from src.nlp.synthetic_detector import SyntheticDetector, SyntheticForensicReport
from src.nlp.temporal_decay import calculate_temporal_decay

__all__ = [
    "calculate_temporal_decay",
    "ClaimDecomposer",
    "PreflightAuditor",
    "PreflightAuditReport",
    "SyntheticDetector",
    "SyntheticForensicReport",
]
