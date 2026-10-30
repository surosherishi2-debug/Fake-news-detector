"""Adversarial Attack Simulation Suite (TextFooler Heuristic).

Implements adversarial synonym substitution and syntactic perturbation based on
Jin et al. (2020) and survey paper benchmarks to quantify model vulnerability:
Evaluates whether a text-only classifier flips predictions when words are swapped,
and verifies how multimodal graph context shields TruthLens against attacks.
"""

import re
import random
from typing import List, Dict, Any, Tuple

# Context-preserving synonym mapping dictionary for adversarial stress testing
SYNONYM_REPLACEMENTS = {
    "safe": ["riskless", "secure", "harmless", "unhazardous"],
    "effective": ["efficacious", "potent", "competent", "operative"],
    "cure": ["remedy", "panacea", "therapy", "restoration"],
    "approved": ["sanctioned", "endorsed", "certified", "validated"],
    "failing": ["deteriorating", "collapsing", "declining", "slipping"],
    "proven": ["verified", "substantiated", "authenticated", "established"],
    "hacked": ["compromised", "breached", "penetrated", "infiltrated"],
    "crisis": ["emergency", "catastrophe", "predicament", "turmoil"],
    "record": ["unprecedented", "historic", "benchmark", "milestone"],
    "secret": ["covert", "confidential", "undisclosed", "clandestine"],
    "fake": ["fabricated", "counterfeit", "spurious", "inauthentic"],
    "banned": ["prohibited", "interdicted", "outlawed", "disallowed"]
}

class AdversarialAttackSimulator:
    """Generates perturbed adversarial variants of claims using synonym substitution."""

    def __init__(self, synonym_map: Dict[str, List[str]] = None):
        self.synonym_map = synonym_map or SYNONYM_REPLACEMENTS

    def perturb_text(
        self,
        text: str,
        perturbation_budget: float = 0.20
    ) -> Tuple[str, List[Dict[str, str]], float]:
        """
        Perturbs text by substituting target keywords with context-preserving synonyms.

        Args:
            text: Original claim or headline.
            perturbation_budget: Max fraction of words allowed to be modified (default 20%).

        Returns:
            perturbed_text: The transformed sentence.
            substitutions: List of dicts recording {original, replacement, index}.
            modification_rate: Actual percentage of modified words.
        """
        words = re.findall(r"\b\w+\b|[^\w\s]", text)
        eligible_indices = [
            i for i, w in enumerate(words)
            if w.lower() in self.synonym_map and len(w) > 3
        ]

        if not eligible_indices:
            # Fallback: minor paraphrasing prefix if no keyword matches
            return text, [], 0.0

        max_swaps = max(1, int(len(words) * perturbation_budget))
        swap_indices = random.sample(eligible_indices, min(max_swaps, len(eligible_indices)))

        substitutions = []
        perturbed_words = list(words)

        for idx in swap_indices:
            orig = words[idx]
            lower_orig = orig.lower()
            replacement_candidates = self.synonym_map[lower_orig]
            replacement = random.choice(replacement_candidates)
            
            # Preserve capitalization
            if orig.istitle():
                replacement = replacement.capitalize()
            elif orig.isupper():
                replacement = replacement.upper()

            perturbed_words[idx] = replacement
            substitutions.append({
                "original": orig,
                "replacement": replacement,
                "position": idx
            })

        # Reconstruct sentence with punctuation handling
        result_text = ""
        for i, token in enumerate(perturbed_words):
            if re.match(r"[^\w\s]", token):
                result_text = result_text.rstrip() + token + " "
            else:
                result_text += token + " "

        perturbed_final = result_text.strip()
        actual_mod_rate = len(substitutions) / max(1, len(words))

        return perturbed_final, substitutions, round(actual_mod_rate, 4)

