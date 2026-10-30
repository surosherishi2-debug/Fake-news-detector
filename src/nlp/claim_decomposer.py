"""Claim Decomposition and Check-Worthiness Scoring Engine.

Extracts atomic verifiable factual claims C = {c_1, ..., c_k} from unstructured article text
following the ClaimBuster paradigm established in TruthLens Section 3.1.
"""

import re
from typing import List, Tuple
from src.core.types import Claim

# High-frequency linguistic markers of verifiable assertions (ClaimBuster heuristics)
FACT_INDICATORS = [
    r"\b(reported|confirmed|announced|discovered|killed|passed|signed|banned|approved)\b",
    r"\b(percent|%|million|billion|trillion|dollars|\$|rupees|₹)\b",
    r"\b(increased|decreased|surged|dropped|rose|fell|caused|leads to)\b",
    r"\b(study|research|scientists|who|fda|cdc|isro|nasa|parliament|court|supreme court)\b",
    r"\b(\d{1,4}\s*(january|february|march|april|may|june|july|august|september|october|november|december|\d{4}))\b",
]

NON_CLAIM_INDICATORS = [
    r"\b(i think|i believe|in my opinion|maybe|perhaps|it seems|hopefully)\b",
    r"\b(hello|welcome|thank you|good morning|click here|subscribe)\b",
    r"^\s*(what|why|how|when|who|is it|can we)\b",
]

DOMAIN_KEYWORDS = {
    "health": ["vaccine", "virus", "cancer", "hospital", "doctor", "medicine", "covid", "disease", "treatment", "cure"],
    "politics": ["election", "parliament", "congress", "bjp", "president", "minister", "senate", "vote", "government", "policy"],
    "finance": ["market", "economy", "inflation", "gdp", "stock", "bank", "rbi", "interest rate", "revenue", "crypto"],
    "tech": ["ai", "google", "apple", "microsoft", "algorithm", "software", "cyber", "data", "robot"],
}

class ClaimDecomposer:
    """Decomposes unstructured article text into atomic verifiable claims."""

    def __init__(self, min_length: int = 20, check_worthy_threshold: float = 0.5):
        self.min_length = min_length
        self.check_worthy_threshold = check_worthy_threshold

    def decompose(self, text: str) -> List[Claim]:
        """
        Split text into atomic sentences and score each for factual check-worthiness.
        
        Args:
            text: Raw input article or headline.
            
        Returns:
            List[Claim]: Extracted claims exceeding check_worthy_threshold.
        """
        if not text or not text.strip():
            return []

        raw_sentences = self._split_sentences(text)
        claims: List[Claim] = []

        for idx, sentence in enumerate(raw_sentences):
            sentence = sentence.strip()
            if len(sentence) < self.min_length:
                continue

            score, domain, entities = self._evaluate_sentence(sentence)
            if score >= self.check_worthy_threshold:
                claims.append(
                    Claim(
                        text=sentence,
                        index=idx,
                        check_worthiness=round(score, 3),
                        domain=domain,
                        entities=entities,
                    )
                )

        # Fallback: if no individual sentence passed threshold, treat the whole clean text as primary claim
        if not claims and len(text.strip()) >= self.min_length:
            score, domain, entities = self._evaluate_sentence(text.strip())
            claims.append(
                Claim(
                    text=text.strip(),
                    index=0,
                    check_worthiness=round(max(0.6, score), 3),
                    domain=domain,
                    entities=entities,
                )
            )

        return claims

    def _split_sentences(self, text: str) -> List[str]:
        """Split text on sentence boundaries while preserving acronyms and numbers."""
        # Clean newlines and whitespace
        cleaned = re.sub(r"\s+", " ", text)
        # Sentence splitting pattern
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", cleaned)
        return [s for s in sentences if s.strip()]

    def _evaluate_sentence(self, sentence: str) -> Tuple[float, str, List[str]]:
        """Compute check-worthiness score, domain classification, and entity candidates."""
        score = 0.50
        lower = sentence.lower()

        # Boost for factual assertion cues
        for pattern in FACT_INDICATORS:
            if re.search(pattern, lower):
                score += 0.12

        # Penalize for subjective opinion or query structure
        for pattern in NON_CLAIM_INDICATORS:
            if re.search(pattern, lower):
                score -= 0.25

        # Digits/statistics strongly indicate verifiable facts
        if re.search(r"\d+", sentence):
            score += 0.10

        # Domain inference
        detected_domain = "general"
        max_matches = 0
        for domain, keywords in DOMAIN_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in lower)
            if matches > max_matches:
                max_matches = matches
                detected_domain = domain

        # Simple capitalized entities extraction
        entities = list(set(re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", sentence)))

        clamped_score = max(0.05, min(0.99, score))
        return clamped_score, detected_domain, entities
