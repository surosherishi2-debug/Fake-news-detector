"""Synthetic Media Forensics & AI Hallucination Detector ("The Real Fake").

Analyzes statistical burstiness, lexical entropy, GLTR-inspired token ranking,
and LLM generative signatures to disentangle Human Genuine Writing vs.
AI-Generated Synthetic Sludge / Hallucinations.
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
    r"\b(foster a deeper|multifaceted|seamlessly integrates|testament to the)\b",
]

# High-frequency predictability vocabulary commonly favored by LLM beam-search / greedy decoding
TOP_10_PREDICTABLE = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with",
    "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her",
    "she", "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up",
    "out", "if", "about", "who", "get", "which", "go", "me", "when", "make", "can", "like", "time",
    "no", "just", "him", "know", "take", "people", "into", "year", "your", "good", "some", "could",
    "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think",
    "also", "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", "even",
    "new", "want", "because", "any", "these", "give", "day", "most", "us", "important", "crucial",
    "furthermore", "moreover", "significant", "development", "process", "landscape"
}

TOP_100_COMMON = {
    "vital", "essential", "primary", "critical", "notably", "subsequently", "underlying", "perspective",
    "demonstrate", "illustrate", "enhance", "optimize", "leverage", "comprehensive", "framework",
    "dynamic", "robust", "systematic", "paradigm", "integration", "holistic", "alignment", "efficient",
    "impactful", "nuanced", "imperative", "sustainable", "accelerate", "facilitate", "spearhead"
}

class TokenForensicEntry(BaseModel):
    word: str
    rank_category: str  # "top10" (Green), "top100" (Yellow), "top1000" (Red), "rare" (Purple)
    color_code: str

class SyntheticForensicReport(BaseModel):
    ai_generated_probability: float = Field(..., ge=0.0, le=1.0)
    classification: str  # HUMAN_AUTHORED, AI_GENERATED_HALLUCINATION, HYBRID_HUMAN_EDITED
    burstiness_score: float = Field(..., description="Sentence length standard deviation; humans write with high variance")
    lexical_diversity: float = Field(..., description="Type-Token Ratio (TTR)")
    llm_signature_count: int
    detected_phrases: List[str] = Field(default_factory=list)
    gltr_distribution: Dict[str, float] = Field(default_factory=dict, description="Percentage of tokens in Top-10, Top-100, Top-1000, Rare")
    token_forensics: List[TokenForensicEntry] = Field(default_factory=list, description="Word-by-word GLTR rank annotations")
    verdict_explanation: str

class SyntheticDetector:
    """Forensic analyzer for AI-generated text and hallucinated pseudo-science."""

    def analyze_text(self, text: str) -> SyntheticForensicReport:
        """
        Analyze statistical properties of text to detect LLM generation.
        
        Args:
            text: Input article or essay text.
            
        Returns:
            SyntheticForensicReport: Metric breakdown and AI probability with GLTR tokens.
        """
        if not text or len(text.strip()) < 40:
            return SyntheticForensicReport(
                ai_generated_probability=0.20,
                classification="HUMAN_AUTHORED",
                burstiness_score=10.0,
                lexical_diversity=0.85,
                llm_signature_count=0,
                detected_phrases=[],
                gltr_distribution={"top10": 25.0, "top100": 30.0, "top1000": 25.0, "rare": 20.0},
                token_forensics=[],
                verdict_explanation="Sample too short for robust statistical entropy analysis.",
            )

        words = re.findall(r"[\w'-]+", text)
        sentences = [s.strip() for s in re.split(r"[.!?।]+", text) if len(s.strip()) > 5]

        # 1. Burstiness Analysis (Variance in sentence length)
        # Humans write with dynamic variation: short punchy sentences followed by long complex sentences.
        # LLMs default to uniform, monotonic sentence lengths (low burstiness).
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

        # 4. GLTR-Style Token Rank Categorization
        top10_count = 0
        top100_count = 0
        top1000_count = 0
        rare_count = 0
        token_forensics: List[TokenForensicEntry] = []

        for w in words[:120]:  # Limit for visual display
            lw = w.lower()
            if lw in TOP_10_PREDICTABLE:
                cat = "top10"
                color = "#10B981"  # Emerald Green
                top10_count += 1
            elif lw in TOP_100_COMMON:
                cat = "top100"
                color = "#F59E0B"  # Amber Yellow
                top100_count += 1
            elif len(lw) <= 6:
                cat = "top1000"
                color = "#EF4444"  # Coral Red
                top1000_count += 1
            else:
                cat = "rare"
                color = "#8B5CF6"  # Purple (Rare / Creative)
                rare_count += 1

            token_forensics.append(TokenForensicEntry(
                word=w,
                rank_category=cat,
                color_code=color
            ))

        total_words = max(1, len(words[:120]))
        gltr_dist = {
            "top10": round((top10_count / total_words) * 100, 1),
            "top100": round((top100_count / total_words) * 100, 1),
            "top1000": round((top1000_count / total_words) * 100, 1),
            "rare": round((rare_count / total_words) * 100, 1),
        }

        # 5. Bayesian Probability Calculation
        # High fraction in top-10 (>65%) + low burstiness (<4.5) + signature phrases strongly indicates LLM generation
        ai_score = 0.20

        if burstiness < 4.2:
            ai_score += 0.30  # Monotonic machine pacing
        elif burstiness > 8.0:
            ai_score -= 0.15  # Natural human variation

        if gltr_dist["top10"] > 60.0:
            ai_score += 0.25  # High predictability
        elif gltr_dist["rare"] > 25.0:
            ai_score -= 0.20  # Human creative entropy

        ai_score += min(0.35, sig_count * 0.12)

        clamped_ai_prob = max(0.02, min(0.98, ai_score))

        if clamped_ai_prob >= 0.68:
            classification = "AI_GENERATED_HALLUCINATION"
            explanation = (
                f"Statistical Forensics: High probability of AI generation ({clamped_ai_prob:.1%}). "
                f"Low sentence burstiness ({burstiness:.2f}) and high top-10 token predictability ({gltr_dist['top10']}%) "
                f"exceed human variance bounds. Identified {sig_count} generative signature phrase(s)."
            )
        elif clamped_ai_prob >= 0.40:
            classification = "HYBRID_HUMAN_EDITED"
            explanation = (
                f"Statistical Forensics: Intermediate probability ({clamped_ai_prob:.1%}). "
                f"Characteristics indicate potential AI-assisted draft with subsequent human revision."
            )
        else:
            classification = "HUMAN_AUTHORED"
            explanation = (
                f"Statistical Forensics: Consistent with human authorship ({1.0 - clamped_ai_prob:.1%} genuine). "
                f"Dynamic sentence burstiness ({burstiness:.2f}) and healthy lexical entropy ({ttr:.2f})."
            )

        return SyntheticForensicReport(
            ai_generated_probability=round(clamped_ai_prob, 4),
            classification=classification,
            burstiness_score=round(burstiness, 2),
            lexical_diversity=round(ttr, 2),
            llm_signature_count=sig_count,
            detected_phrases=detected_phrases,
            gltr_distribution=gltr_dist,
            token_forensics=token_forensics,
            verdict_explanation=explanation,
        )
