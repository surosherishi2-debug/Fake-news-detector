"""TruthLens-Omni Tri-Modal Fusion Engine.

Integrates:
1. Claim-Evidence Alignment Module (CEAM) with temporal decay w(t)
2. Propagation Graph Encoder (PGE) for cascade topology
3. Publisher Historical Credibility
"""

import time
from typing import List, Optional, Tuple
from datetime import datetime, timezone
from src.core.types import (
    Claim,
    Evidence,
    ClaimEvidenceAlignment,
    ClaimStance,
    VerificationVerdict,
    VerificationResult,
    VerificationRequest,
)
from src.nlp.claim_decomposer import ClaimDecomposer
from src.retrieval.fact_check_client import FactCheckClient
from src.graph.hgt_encoder import CascadeTopologyAnalyzer

# Known domain credibility registry (NewsGuard-style baseline criteria)
TRUSTED_PUBLISHERS = {
    "reuters.com": 0.95,
    "apnews.com": 0.95,
    "bbc.com": 0.90,
    "pib.gov.in": 0.92,
    "who.int": 0.96,
    "nature.com": 0.98,
    "factcheck.org": 0.92,
}

UNTRUSTED_PUBLISHERS = {
    "thepatriotnews247.xyz": 0.10,
    "dailyconspiracy.net": 0.15,
    "breaking-viral-updates.co": 0.20,
}

class TruthLensEngine:
    """The central end-to-end verification engine."""

    def __init__(
        self,
        claim_decomposer: Optional[ClaimDecomposer] = None,
        fact_checker: Optional[FactCheckClient] = None,
        graph_analyzer: Optional[CascadeTopologyAnalyzer] = None,
    ):
        self.decomposer = claim_decomposer or ClaimDecomposer()
        self.fact_checker = fact_checker or FactCheckClient()
        self.graph_analyzer = graph_analyzer or CascadeTopologyAnalyzer()

    def verify(self, request: VerificationRequest) -> VerificationResult:
        """
        Execute end-to-end verification across CEAM, PGE, and Publisher modules.
        
        Args:
            request: VerificationRequest containing article text, metadata, and optional cascade.
            
        Returns:
            VerificationResult: Calibrated classification verdict, confidence, and provenance chain.
        """
        start_time = time.perf_counter()
        now = request.publication_date or datetime.now(timezone.utc)

        # 1. Decompose input into atomic claims
        claims = self.decomposer.decompose(request.text)

        # 2. Retrieve evidence & compute CEAM alignments
        alignments: List[ClaimEvidenceAlignment] = []
        refute_scores: List[float] = []
        support_scores: List[float] = []

        for claim in claims:
            evidences = self.fact_checker.search_evidence(claim.text, claim_time=now, max_results=3)
            for ev in evidences:
                stance = self._infer_stance(claim.text, ev)
                alignment_score = ev.final_score  # Includes semantic similarity * temporal weight w(t)

                alignments.append(
                    ClaimEvidenceAlignment(
                        claim=claim,
                        evidence=ev,
                        alignment_score=alignment_score,
                        stance=stance,
                    )
                )

                if stance == ClaimStance.REFUTES:
                    refute_scores.append(alignment_score)
                elif stance == ClaimStance.SUPPORTS:
                    support_scores.append(alignment_score)

        # 3. Analyze social cascade (PGE)
        graph_metrics = self.graph_analyzer.analyze_cascade(request.cascade)
        graph_risk = graph_metrics["cascade_risk_score"]

        # 4. Evaluate publisher historical trust
        pub_trust = self._evaluate_publisher_trust(request.publisher)

        # 5. Tri-modal attention fusion
        semantic_refute = max(refute_scores) if refute_scores else 0.0
        semantic_support = max(support_scores) if support_scores else 0.0

        # Weights: α (CEAM) = 0.55, β (Cascade PGE) = 0.25, γ (Publisher) = 0.20
        fake_probability = (
            0.55 * semantic_refute
            + 0.25 * graph_risk
            + 0.20 * (1.0 - pub_trust)
        )

        real_probability = (
            0.55 * semantic_support
            + 0.25 * (1.0 - graph_risk)
            + 0.20 * pub_trust
        )

        # Determine verdict and confidence
        if (fake_probability >= 0.50 or (semantic_refute >= 0.50 and fake_probability > real_probability)) and fake_probability > real_probability:
            verdict = VerificationVerdict.FAKE
            confidence = min(0.98, max(fake_probability, semantic_refute))
            explanation = (
                f"Article identified as likely FAKE (confidence: {confidence:.1%}). "
                f"Evidence refutation score: {semantic_refute:.2f}, "
                f"Cascade polarization risk: {graph_risk:.2f}, "
                f"Publisher credibility score: {pub_trust:.2f}."
            )
        elif real_probability >= 0.55 and real_probability > fake_probability:
            verdict = VerificationVerdict.REAL
            confidence = min(0.98, max(real_probability, semantic_support))
            explanation = (
                f"Article verified as authentic REAL news (confidence: {confidence:.1%}). "
                f"External corroboration support: {semantic_support:.2f}, "
                f"Low-polarization normal diffusion risk: {graph_risk:.2f}."
            )
        else:
            verdict = VerificationVerdict.UNCERTAIN
            confidence = round(1.0 - abs(fake_probability - real_probability), 3)
            explanation = (
                "Insufficient conclusive corroboration found in verified registries. "
                "Contextual evidence is mixed or pending human bridging consensus."
            )

        # Provenance chain construction
        provenance = [
            f"Decomposed {len(claims)} atomic verifiable claims.",
            f"Matched {len(alignments)} temporal fact-checking evidence items.",
            f"Propagation graph: {graph_metrics['verified_ratio']:.1%} verified user ratio, CIB anomaly {graph_metrics['cib_anomaly']:.2f}.",
            f"Publisher trust rating: {pub_trust:.2f}.",
        ]

        latency = round((time.perf_counter() - start_time) * 1000.0, 2)

        return VerificationResult(
            verdict=verdict,
            confidence_score=round(confidence, 3),
            semantic_score=round(semantic_refute if verdict == VerificationVerdict.FAKE else semantic_support, 3),
            graph_anomaly_score=round(graph_risk, 3),
            publisher_trust_score=round(pub_trust, 3),
            claims=claims,
            alignments=alignments,
            explanation=explanation,
            provenance_chain=provenance,
            latency_ms=latency,
        )

    def _infer_stance(self, claim_text: str, evidence: Evidence) -> ClaimStance:
        """Infer whether evidence supports or refutes the claim based on ClaimReview rating cues."""
        snippet_lower = evidence.snippet.lower()
        if any(term in snippet_lower for term in ["false", "debunk", "misleading", "fabricated", "untrue", "pants on fire"]):
            return ClaimStance.REFUTES
        if any(term in snippet_lower for term in ["true", "confirmed", "verified", "correct"]):
            return ClaimStance.SUPPORTS
        return ClaimStance.NEUTRAL

    def _evaluate_publisher_trust(self, publisher: Optional[str]) -> float:
        """Lookup publisher domain in credibility index with neutral fallback."""
        if not publisher:
            return 0.50
        cleaned = publisher.lower().strip()
        for domain, score in TRUSTED_PUBLISHERS.items():
            if domain in cleaned:
                return score
        for domain, score in UNTRUSTED_PUBLISHERS.items():
            if domain in cleaned:
                return score
        return 0.50
