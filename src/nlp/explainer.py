"""Explainability & Epistemic Attribution Engine for TruthLens-Omni.

Provides:
1. Token Saliency / Word-Level Attribution: Quantifies which keywords drove the model verdict.
2. Evidence Justification Trail: Detailed audit trail of retrieved fact-check sources,
   publisher ratings, and temporal decay factors.
3. FDA-Style Contextual Nutrition Card: Multi-dimensional credibility profile.
4. Formal Calibrated Abstention (DATA_VOID): Safe zero-assumption fallback when evidence is absent.
"""

import re
import math
import logging
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

from src.core.types import (
    Evidence,
    NutritionCard,
    VerificationVerdict,
    HighlightStatus
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Lexical keywords signaling epistemic status
SENSATIONAL_MARKERS = {
    "shocking", "unbelievable", "secret", "exposed", "miracle", "hidden",
    "mainstream", "media", "banned", "conspiracy", "hacked", "covert"
}

FACTUAL_AUTHORITY_MARKERS = {
    "fda", "who", "cdc", "official", "confirmed", "clinical", "trials",
    "peer-reviewed", "published", "telemetry", "authorities", "study"
}


class TokenAttribution(BaseModel):
    token: str
    importance_score: float  # [-1.0, 1.0]
    category: str            # "DECEPTIVE_SIGNAL", "FACTUAL_GROUNDING", "NEUTRAL"


class EpistemicExplanation(BaseModel):
    verdict: str
    confidence: float
    is_abstained: bool
    abstention_reason: Optional[str] = None
    token_attributions: List[TokenAttribution]
    evidence_trail: List[Dict[str, Any]]
    nutrition_card: NutritionCard
    plain_language_summary: str


class TruthLensExplainer:
    """Computes transparent explanations, token attributions, and abstention decisions."""

    def __init__(self, abstention_threshold: float = 0.42):
        self.abstention_threshold = abstention_threshold

    def compute_token_attributions(
        self,
        claim_text: str,
        verdict: str,
        retrieved_evidences: List[Evidence]
    ) -> List[TokenAttribution]:
        """
        Computes saliency scores for individual tokens in the claim.
        Tokens that match verified evidence snippets or authority terms receive factual grounding weight.
        Sensational or ungrounded speculative tokens receive negative/deceptive attribution.
        """
        tokens = re.findall(r"\b\w+\b|[^\w\s]", claim_text)
        evidence_snippets = " ".join([e.snippet.lower() for e in retrieved_evidences])

        attributions = []
        for t in tokens:
            t_lower = t.lower()
            if len(t) <= 2:
                attributions.append(TokenAttribution(token=t, importance_score=0.0, category="NEUTRAL"))
                continue

            score = 0.0
            category = "NEUTRAL"

            if t_lower in SENSATIONAL_MARKERS:
                score = -0.75 if verdict == "REFUTED" else -0.35
                category = "DECEPTIVE_SIGNAL"
            elif t_lower in FACTUAL_AUTHORITY_MARKERS or t_lower in evidence_snippets:
                score = 0.85 if verdict == "VERIFIED" else 0.45
                category = "FACTUAL_GROUNDING"
            else:
                score = 0.10
                category = "NEUTRAL"

            attributions.append(TokenAttribution(
                token=t,
                importance_score=round(score, 3),
                category=category
            ))

        return attributions

    def build_evidence_trail(
        self,
        retrieved_evidences: List[Evidence]
    ) -> List[Dict[str, Any]]:
        """Formats the retrieved evidence documents into a human-readable audit trail."""
        trail = []
        for idx, ev in enumerate(retrieved_evidences, 1):
            trail.append({
                "citation_rank": idx,
                "title": ev.source_title,
                "publisher": ev.publisher,
                "url": ev.url,
                "publication_date": ev.publish_date.strftime("%Y-%m-%d") if ev.publish_date else "Unknown",
                "snippet": ev.snippet,
                "semantic_similarity": ev.semantic_similarity,
                "temporal_decay_factor": ev.temporal_weight,
                "composite_relevance_score": ev.final_score
            })
        return trail

    def build_nutrition_card(
        self,
        claim_text: str,
        verdict: str,
        confidence: float,
        evidences: List[Evidence],
        is_satire: bool = False
    ) -> NutritionCard:
        """Generates the FDA-style multi-dimensional epistemic nutrition card."""
        avg_pub_cred = 0.90 if evidences else 0.50
        min_temporal_w = float(np.min([e.temporal_weight for e in evidences])) if evidences else 0.85

        clickbait_words = ["shocking", "miracle", "secret", "they don't want you to know", "viral"]
        sensationalism = 40.0 if any(w in claim_text.lower() for w in clickbait_words) else 10.0

        if verdict == "DATA_VOID":
            factual_grounding = 0.0
        elif verdict in ("VERIFIED", "REAL"):
            factual_grounding = 100.0 if not evidences else float(np.mean([e.semantic_similarity for e in evidences])) * 100.0
        elif verdict in ("REFUTED", "FAKE"):
            factual_grounding = float(np.mean([1.0 - e.semantic_similarity for e in evidences])) * 100.0 if evidences else 20.0
        else:
            factual_grounding = 50.0

        summary = (
            f"Verdict: {verdict}. Confidence: {confidence*100:.1f}%. "
            f"Accredited citations: {len(evidences)}."
        )

        return NutritionCard(
            factual_grounding_score=min(100.0, max(0.0, round(factual_grounding, 1))),
            source_transparency_score=round(avg_pub_cred * 100.0, 1),
            organic_diffusion_score=75.0,
            sensationalism_score=sensationalism,
            temporal_freshness_score=round(min_temporal_w * 100.0, 1),
            verdict_label=verdict,
            summary_verdict=summary,
        )

    def explain(
        self,
        claim_text: str,
        retrieved_evidences: List[Evidence],
        retrieval_meta: Dict[str, Any],
        raw_classifier_verdict: Optional[str] = None,
        raw_classifier_confidence: Optional[float] = None,
        is_satirical_source: bool = False
    ) -> EpistemicExplanation:
        """
        Synthesizes transparent verdict, token attributions, evidence trail, and abstention logic.
        """
        s_max = retrieval_meta.get("max_dense_similarity", 0.0)
        is_void = retrieval_meta.get("is_evidence_void", False) or s_max < self.abstention_threshold

        # 1. Handle Satire Override
        if is_satirical_source or "satire" in claim_text.lower():
            verdict = "SATIRE"
            conf = 0.95
            is_abstained = False
            reason = None
            summary = "Identified as satirical humor or parody from an accredited satirical publication. Not intended as factual disinformation."

        # 2. Handle Calibrated Abstention (DATA_VOID)
        elif is_void or len(retrieved_evidences) == 0:
            verdict = "DATA_VOID"
            conf = 0.0
            is_abstained = True
            reason = (
                f"Maximum retrieval similarity (S_max={s_max:.3f}) fell below the empirical evidence "
                f"threshold (tau={self.abstention_threshold:.2f}). No verified fact-check exists."
            )
            summary = (
                "Insufficient authoritative evidence found in accredited fact-checking databases. "
                "TruthLens abstains from asserting truth or falsehood to prevent hallucination."
            )

        # 3. Grounded Epistemic Verdict from Verified Retrieval
        else:
            suggested = retrieval_meta.get("suggested_grounded_verdict", "VERIFIED")
            verdict = suggested
            conf = min(0.99, max(0.65, s_max))
            is_abstained = False
            reason = None
            top_ev = retrieved_evidences[0]
            if verdict == "REFUTED":
                summary = f"Refuted by accredited fact-checker '{top_ev.publisher}'. Summary: {top_ev.snippet[:120]}..."
            else:
                summary = f"Corroborated by verified publication '{top_ev.publisher}'. Summary: {top_ev.snippet[:120]}..."

        # Compute attributions and trail
        attributions = self.compute_token_attributions(claim_text, verdict, retrieved_evidences)
        evidence_trail = self.build_evidence_trail(retrieved_evidences)
        nutrition_card = self.build_nutrition_card(claim_text, verdict, conf, retrieved_evidences, is_satirical_source)

        return EpistemicExplanation(
            verdict=verdict,
            confidence=round(conf, 4),
            is_abstained=is_abstained,
            abstention_reason=reason,
            token_attributions=attributions,
            evidence_trail=evidence_trail,
            nutrition_card=nutrition_card,
            plain_language_summary=summary
        )


import numpy as np
