"""Core package initialization."""

from src.core.config import settings
from src.core.types import (
    Claim,
    Evidence,
    ClaimEvidenceAlignment,
    ClaimStance,
    VerificationVerdict,
    VerificationResult,
    VerificationRequest,
    SocialCascade,
    SocialNode,
    SocialEdge,
    NodeType,
    RelationType,
)

__all__ = [
    "settings",
    "Claim",
    "Evidence",
    "ClaimEvidenceAlignment",
    "ClaimStance",
    "VerificationVerdict",
    "VerificationResult",
    "VerificationRequest",
    "SocialCascade",
    "SocialNode",
    "SocialEdge",
    "NodeType",
    "RelationType",
]
