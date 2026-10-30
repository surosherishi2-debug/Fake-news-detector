"""Data schemas and type contracts for TruthLens-Omni."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class VerificationVerdict(str, Enum):
    """3-way classification outcome defined in TruthLens."""
    REAL = "REAL"
    FAKE = "FAKE"
    UNCERTAIN = "UNCERTAIN"

class ClaimStance(str, Enum):
    """NLI stance of evidence relative to a claim."""
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    NEUTRAL = "NEUTRAL"

class Claim(BaseModel):
    """Atomic factual assertion extracted from raw content."""
    text: str = Field(..., description="Atomic claim statement")
    index: int = Field(default=0, description="Order index in parent text")
    check_worthiness: float = Field(default=0.8, ge=0.0, le=1.0, description="Likelihood of being a check-worthy fact")
    domain: Optional[str] = Field(default="general", description="Identified domain (e.g. politics, health, tech)")
    entities: List[str] = Field(default_factory=list, description="Named entities mentioned in claim")

class Evidence(BaseModel):
    """Retrieved external fact-checking document or sentence."""
    source_title: str
    publisher: str
    url: Optional[str] = None
    publish_date: Optional[datetime] = None
    snippet: str
    semantic_similarity: float = Field(default=0.8, ge=0.0, le=1.0)
    temporal_weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Decay weight w(t) based on age")
    final_score: float = Field(default=0.8, ge=0.0, le=1.0)

class ClaimEvidenceAlignment(BaseModel):
    """CEAM alignment score and NLI stance for a single claim-evidence pair."""
    claim: Claim
    evidence: Evidence
    alignment_score: float = Field(..., ge=0.0, le=1.0)
    stance: ClaimStance = ClaimStance.NEUTRAL

class NodeType(str, Enum):
    ARTICLE = "article"
    USER = "user"
    PUBLISHER = "publisher"

class RelationType(str, Enum):
    SHARES = "shares"
    FOLLOWS = "follows"
    AUTHORED_BY = "authored_by"

class SocialNode(BaseModel):
    id: str
    type: NodeType
    name: Optional[str] = None
    verified: bool = False
    follower_count: int = 0
    features: List[float] = Field(default_factory=list)

class SocialEdge(BaseModel):
    source: str
    target: str
    relation: RelationType
    timestamp: Optional[datetime] = None

class SocialCascade(BaseModel):
    """Heterogeneous social propagation graph."""
    article_id: str
    nodes: List[SocialNode] = Field(default_factory=list)
    edges: List[SocialEdge] = Field(default_factory=list)
    cib_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Coordinated inauthentic behavior indicator")

class VerificationRequest(BaseModel):
    """Request payload for real-time article verification."""
    text: str = Field(..., min_length=5, description="Full article or headline text")
    publisher: Optional[str] = Field(default=None, description="Publisher name or domain")
    publication_date: Optional[datetime] = Field(default=None, description="Publication timestamp")
    cascade: Optional[SocialCascade] = Field(default=None, description="Optional social graph propagation data")

class VerificationResult(BaseModel):
    """End-to-end verification report from TruthLens-Omni."""
    verdict: VerificationVerdict
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    semantic_score: float = Field(..., ge=0.0, le=1.0, description="Content semantics alignment score")
    graph_anomaly_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Social cascade polarization score")
    publisher_trust_score: float = Field(default=0.5, ge=0.0, le=1.0)
    claims: List[Claim] = Field(default_factory=list)
    alignments: List[ClaimEvidenceAlignment] = Field(default_factory=list)
    explanation: str
    provenance_chain: List[str] = Field(default_factory=list)
    latency_ms: float = 0.0
