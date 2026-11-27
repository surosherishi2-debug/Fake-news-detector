"""Data schemas and type contracts for TruthLens-Omni."""

from datetime import datetime
from enum import StrEnum
from typing import List

from pydantic import BaseModel, Field


class VerificationVerdict(StrEnum):
    """3-way classification outcome defined in TruthLens."""

    REAL = "REAL"
    FAKE = "FAKE"
    UNCERTAIN = "UNCERTAIN"


class ClaimStance(StrEnum):
    """NLI stance of evidence relative to a claim."""

    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    NEUTRAL = "NEUTRAL"


class HighlightStatus(StrEnum):
    VERIFIED = "VERIFIED"  # 🟢 Verified true by accredited source
    REFUTED = "REFUTED"  # 🔴 Debunked / Fabricated
    DATA_VOID = "DATA_VOID"  # 🟡 Unverified / Pending corroboration
    OPINION = "OPINION"  # ⚪ Subjective / Rhetoric


class Claim(BaseModel):
    """Atomic factual assertion extracted from raw content."""

    text: str = Field(..., description="Atomic claim statement")
    index: int = Field(default=0, description="Order index in parent text")
    check_worthiness: float = Field(default=0.8, ge=0.0, le=1.0, description="Likelihood of being a check-worthy fact")
    domain: str | None = Field(default="general", description="Identified domain (e.g. politics, health, tech)")
    entities: List[str] = Field(default_factory=list, description="Named entities mentioned in claim")
    highlight_status: HighlightStatus = Field(default=HighlightStatus.DATA_VOID)
    citation: str | None = None


class Evidence(BaseModel):
    """Retrieved external fact-checking document or sentence."""

    source_title: str
    publisher: str
    url: str | None = None
    publish_date: datetime | None = None
    snippet: str
    semantic_similarity: float = Field(default=0.8, ge=0.0, le=1.0)
    temporal_weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Decay weight w(t) based on age")
    final_score: float = Field(default=0.8, ge=0.0, le=1.0)
    grounded_verdict: str | None = Field(
        default=None, description="Accredited ClaimReview verdict (REFUTED, VERIFIED, SATIRICAL)"
    )


class ClaimEvidenceAlignment(BaseModel):
    """CEAM alignment score and NLI stance for a single claim-evidence pair."""

    claim: Claim
    evidence: Evidence
    alignment_score: float = Field(..., ge=0.0, le=1.0)
    stance: ClaimStance = ClaimStance.NEUTRAL


class NodeType(StrEnum):
    ARTICLE = "article"
    USER = "user"
    PUBLISHER = "publisher"


class RelationType(StrEnum):
    SHARES = "shares"
    FOLLOWS = "follows"
    AUTHORED_BY = "authored_by"


class SocialNode(BaseModel):
    id: str
    type: NodeType
    name: str | None = None
    verified: bool = False
    follower_count: int = 0
    features: List[float] = Field(default_factory=list)


class SocialEdge(BaseModel):
    source: str
    target: str
    relation: RelationType
    timestamp: datetime | None = None


class SocialCascade(BaseModel):
    """Heterogeneous social propagation graph."""

    article_id: str
    nodes: List[SocialNode] = Field(default_factory=list)
    edges: List[SocialEdge] = Field(default_factory=list)
    cib_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Coordinated inauthentic behavior indicator")


class NutritionCard(BaseModel):
    """Contextual 5-dimension credibility scorecard (Feature 1)."""

    factual_grounding_score: float = Field(..., ge=0.0, le=100.0, description="Percentage of claims backed by evidence")
    source_transparency_score: float = Field(
        ..., ge=0.0, le=100.0, description="Publisher credibility and domain trust"
    )
    organic_diffusion_score: float = Field(..., ge=0.0, le=100.0, description="Propagation naturalness vs botnet burst")
    sensationalism_score: float = Field(
        ..., ge=0.0, le=100.0, description="Presence of emotional bait / clickbait cues"
    )
    temporal_freshness_score: float = Field(..., ge=0.0, le=100.0, description="Evidence recency based on w(t)")
    verdict_label: str
    summary_verdict: str


class VerificationRequest(BaseModel):
    """Request payload for real-time article verification."""

    text: str = Field(..., min_length=5, description="Full article or headline text")
    publisher: str | None = Field(default=None, description="Publisher name or domain")
    publication_date: datetime | None = Field(default=None, description="Publication timestamp")
    category: str | None = Field(default=None, description="Domain or news category for adaptive decay")
    cascade: SocialCascade | None = Field(default=None, description="Optional social graph propagation data")


class VerificationResult(BaseModel):
    """End-to-end verification report from TruthLens-Omni."""

    verdict: VerificationVerdict
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    semantic_score: float = Field(..., ge=0.0, le=1.0, description="Content semantics alignment score")
    graph_anomaly_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Social cascade polarization score")
    publisher_trust_score: float = Field(default=0.5, ge=0.0, le=1.0)
    claims: List[Claim] = Field(default_factory=list)
    alignments: List[ClaimEvidenceAlignment] = Field(default_factory=list)
    nutrition_card: NutritionCard | None = None
    explanation: str
    provenance_chain: List[str] = Field(default_factory=list)
    latency_ms: float = 0.0
