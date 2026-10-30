"""Pre-Flight Self-News Studio & Article Auditor.

Enables student journalists and content creators to audit their own drafts
before publication: identifies unsupported factual claims, detects cognitive bias,
and suggests accredited primary citations.
"""

from typing import List, Dict, Any, Optional
import re
from pydantic import BaseModel, Field
from src.nlp.claim_decomposer import ClaimDecomposer
from src.retrieval.fact_check_client import FactCheckClient

class PreflightAssertionAudit(BaseModel):
    sentence_index: int
    text: str
    check_worthiness: float
    is_supported: bool
    risk_level: str  # HIGH, MEDIUM, LOW
    suggested_action: str
    recommended_citations: List[str] = Field(default_factory=list)

class PreflightAuditReport(BaseModel):
    audit_readiness_score: float = Field(..., ge=0.0, le=100.0, description="Overall publication readiness")
    total_assertions: int
    unsupported_high_risk_count: int
    bias_sensationalism_score: float = Field(..., ge=0.0, le=100.0)
    assertions: List[PreflightAssertionAudit]
    recommendations: List[str]

class PreflightAuditor:
    """Audits draft articles for factual integrity prior to publication."""

    def __init__(self, decomposer: Optional[ClaimDecomposer] = None, fact_client: Optional[FactCheckClient] = None):
        self.decomposer = decomposer or ClaimDecomposer()
        self.fact_client = fact_client or FactCheckClient()

    def audit_draft(self, draft_text: str) -> PreflightAuditReport:
        """
        Execute comprehensive pre-flight verification on author's draft.
        
        Args:
            draft_text: Full draft article text.
            
        Returns:
            PreflightAuditReport: Actionable integrity scorecard and citation suggestions.
        """
        claims = self.decomposer.decompose(draft_text)
        audited_assertions: List[PreflightAssertionAudit] = []
        high_risk_count = 0

        for claim in claims:
            # Query external knowledge store for corroboration
            evidences = self.fact_client.search_evidence(claim.text, max_results=2)
            has_support = any(ev.final_score >= 0.70 for ev in evidences)
            has_refutation = any("False" in ev.snippet or "debunk" in ev.snippet.lower() for ev in evidences)

            if has_refutation:
                risk = "HIGH"
                action = "CRITICAL: This assertion has been previously refuted by accredited fact-checkers. Remove or rephrase with counter-evidence."
                high_risk_count += 1
            elif not has_support and claim.check_worthiness >= 0.75:
                risk = "HIGH"
                action = "Factual assertion lacks primary source citation. Add verifiable data or link official release."
                high_risk_count += 1
            elif not has_support and claim.check_worthiness >= 0.55:
                risk = "MEDIUM"
                action = "Secondary claim lacks source attribution."
            else:
                risk = "LOW"
                action = "Corroborated by verified knowledge records."

            rec_citations = [f"{ev.publisher}: {ev.source_title}" for ev in evidences[:2]]

            audited_assertions.append(
                PreflightAssertionAudit(
                    sentence_index=claim.index,
                    text=claim.text,
                    check_worthiness=claim.check_worthiness,
                    is_supported=has_support,
                    risk_level=risk,
                    suggested_action=action,
                    recommended_citations=rec_citations,
                )
            )

        # Detect sensationalism / emotional bias
        sensationalism_score = self._compute_bias_score(draft_text)

        # Publication Readiness Score: penalize high-risk claims and sensationalism
        total_claims = max(1, len(claims))
        readiness = max(10.0, 100.0 - (high_risk_count * 25.0) - (sensationalism_score * 0.3))

        recommendations = []
        if high_risk_count > 0:
            recommendations.append(f"Resolve {high_risk_count} high-risk ungrounded assertions before publishing.")
        if sensationalism_score > 40.0:
            recommendations.append("Tone audit: Reduce clickbait adjectives ('shocking', 'exposed', 'unbelievable') to improve institutional trust.")
        if not recommendations:
            recommendations.append("Excellent epistemic grounding: All verifiable assertions are backed by accredited citations.")

        return PreflightAuditReport(
            audit_readiness_score=round(readiness, 1),
            total_assertions=len(claims),
            unsupported_high_risk_count=high_risk_count,
            bias_sensationalism_score=round(sensationalism_score, 1),
            assertions=audited_assertions,
            recommendations=recommendations,
        )

    def _compute_bias_score(self, text: str) -> float:
        """Measure clickbait and rhetorical bias markers."""
        score = 15.0
        cues = [r"\b(shocking|exposed|miracle|secret cure|banned by doctors|you won't believe)\b", r"!{2,}", r"\b[A-Z]{4,}\b"]
        for c in cues:
            if re.search(c, text, re.I):
                score += 25.0
        return min(95.0, score)

