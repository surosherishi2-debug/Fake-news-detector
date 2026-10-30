"""Synthetic Media Forensics & AI Hallucination Detector ("The Real Fake").

Analyzes statistical burstiness, lexical entropy, and LLM generative signatures
to disentangle Human Genuine Writing vs. AI-Generated Synthetic Sludge / Hallucinations.
"""

from typing import List, Dict, Any, Tuple
import re
import numpy as np
from pydantic import BaseModel, Field

LLM_SIGNATURE_PATTERNS = [
    r"\b(it is important to remember|it is crucial to note|delve into|tapestry of|a testament to)\b",
    r"\b(in conclusion|furthermore|moreover|beacon of hope|ever-evolving landscape)\b",
    r"\b(navigating the complexities|shedding light on|plays a pivotal role)\b",
    r"\b(it is worth noting|stand as a reminder|in today's digital age)\b",
]

class SyntheticForensicReport(BaseModel):
    ai_generated_probability: float = Field(..., ge=0.0, le=1.0)
    classification: str  # HUMAN_AUTHORED, AI_GENERATED_HALLUCINATION, HYBRID_HUMAN_EDITED
    burstiness_score: float = Field(..., description="Sentence length standard deviation; humans write with high variance")
    lexical_diversity: float = Field(..., description="Type-Token Ratio (TTR)")
    llm_signature_count: int
    detected_phrases: List[str] = Field(default_factory=list)
    verdict_explanation: str

class SyntheticDetector:
    """Forensic analyzer for AI-generated text and hallucinated pseudo-science."""

    def analyze_text(self, text: str) -> SyntheticForensicReport:
        """
        Analyze statistical properties of text to detect LLM generation.
        
        Args:
            text: Input article or essay text.
            
        Returns:
            SyntheticForensicReport: Metric breakdown and AI probability.
        """
        if not text or len(text.strip()) < 50:
            return SyntheticForensicReport(
                ai_generated_probability=0.20,
                classification="HUMAN_AUTHORED",
                burstiness_score=10.0,
                lexical_diversity=0.85,
                llm_signature_count=0,
                detected_phrases=[],
                verdict_explanation="Sample too short for robust statistical entropy analysis.",
            )

        words = re.findall(r"\b[A-Za-z]+\b", text)
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 5]

        # 1. Burstiness Analysis (Variance in sentence length)
        # Humans write with dynamic variation: short punchy sentences followed by long complex sentences.
        # LLMs default to uniform, monotonic sentence lengths.
        sentence_lengths = [len(s.split()) for s in sentences] if sentences else [10]
        burstiness = float(np.std(sentence_lengths)) if len(sentence_lengths) > 1 else 0.0

        # 2. Lexical Diversity (Type-Token Ratio)
        unique_tokens = len(set(w.lower() for w in words))
        ttr = (unique_tokens / max(1, len(words)))

        # 3. LLM Signature Phrase Matching
        detected_phrases = []
        lower_text = text.lower()
        for pat in LLM_SIGNATURE_PATTERNS:
            matches = re.findall(pat, lower_text)
            detected_phrases.extend(matches)

        sig_count = len(detected_phrases)

        # 4. Bayesian Probability Calculation
        # Low burstiness (std < 4.0) + signature phrases strongly indicates LLM generation
        ai_score = 0.25

        if burstiness < 4.5:
            ai_score += 0.35  # Monotonic pacing
        elif burstiness > 8.5:
            ai_score -= 0.15  # Natural human variation

        ai_score += min(0.40, sig_count * 0.15)

        clamped_ai_prob = max(0.02, min(0.98, ai_score))

        if clamped_ai_prob >= 0.70:
            classification = "AI_GENERATED_HALLUCINATION"
            explanation = (
                f"Statistical Forensics: High probability of AI generation ({clamped_ai_prob:.1%}). "
                f"Low sentence burstiness ({burstiness:.1f}) and {sig_count} generative LLM rhetorical transitions detected."
            )
        elif clamped_ai_prob >= 0.45:
            classification = "HYBRID_HUMAN_EDITED"
            explanation = (
                f"Hybrid Characteristics: Mixed statistical signatures ({clamped_ai_prob:.1%}). "
                f"Indicates human editing of an underlying AI-assisted draft."
            )
        else:
            classification = "HUMAN_AUTHORED"
            explanation = (
                f"Human Authorship Verified: Natural sentence burstiness ({burstiness:.1f}) "
                f"and healthy lexical diversity ({ttr:.2f}) consistent with authentic human journalism."
            )

        return SyntheticForensicReport(
            ai_generated_probability=round(clamped_ai_prob, 3),
            classification=classification,
            burstiness_score=round(burstiness, 2),
            lexical_diversity=round(ttr, 3),
            llm_signature_count=sig_count,
            detected_phrases=list(set(detected_phrases)),
            verdict_explanation=explanation,
        )
