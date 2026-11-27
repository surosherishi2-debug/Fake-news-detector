"""Core package initialization."""

from src.core.config import settings
from src.core.types import (
    Claim,
    ClaimEvidenceAlignment,
    ClaimStance,
    Evidence,
    HighlightStatus,
    NodeType,
    NutritionCard,
    RelationType,
    SocialCascade,
    SocialEdge,
    SocialNode,
    VerificationRequest,
    VerificationResult,
    VerificationVerdict,
)

__all__ = [
    "settings",
    "Claim",
    "Evidence",
    "ClaimEvidenceAlignment",
    "ClaimStance",
    "HighlightStatus",
    "NutritionCard",
    "VerificationVerdict",
    "VerificationResult",
    "VerificationRequest",
    "SocialCascade",
    "SocialNode",
    "SocialEdge",
    "NodeType",
    "RelationType",
]
