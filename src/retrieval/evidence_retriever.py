"""Two-Stage Dense Evidence Retrieval & Multi-Factor Re-Ranking Engine.

Architecture:
- Stage 1: Dense Vector Cosine Similarity Search using Pre-trained Sentence Transformers.
- Stage 2: Multi-Factor Re-ranking combining Semantic Similarity, Token Lexical Overlap,
  Publisher Credibility Weight, and Domain-Adaptive Temporal Decay w(t) = exp(-lambda * delta_t).
- Abstention Boundary: Quantifies Maximum Evidence Alignment S_max to trigger calibrated DATA_VOID.
"""

import re
import math
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone

import numpy as np
from sentence_transformers import SentenceTransformer

from src.retrieval.knowledge_store import KnowledgeStore
from src.nlp.temporal_decay import calculate_temporal_decay, get_domain_lambda
from src.core.types import Evidence

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def compute_token_overlap(query: str, doc_text: str) -> float:
    """Compute character & token lexical overlap ratio between query and document (English & Indic)."""
    q_tokens = set(re.findall(r"[\w\u0900-\u097F]{2,}", query.lower()))
    d_tokens = set(re.findall(r"[\w\u0900-\u097F]{2,}", doc_text.lower()))
    if not q_tokens or not d_tokens:
        return 0.0
    return len(q_tokens & d_tokens) / len(q_tokens)


class TwoStageEvidenceRetriever:
    """Two-Stage Dense Retrieval & Temporal Re-Ranking Pipeline."""

    def __init__(
        self,
        knowledge_store: Optional[KnowledgeStore] = None,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        dense_top_k: int = 10,
        rerank_top_m: int = 3,
        abstention_threshold: float = 0.40
    ):
        self.store = knowledge_store or KnowledgeStore()
        self.model_name = model_name
        self.dense_top_k = dense_top_k
        self.rerank_top_m = rerank_top_m
        self.abstention_threshold = abstention_threshold

        # Initialize uniform multilingual encoder
        logger.info(f"Initializing SentenceTransformer encoder: {model_name}...")
        self.encoder = SentenceTransformer(model_name)

    def _is_devanagari(self, text: str) -> bool:
        """Detect if text contains Devanagari script (Hindi/Marathi)."""
        return any("\u0900" <= char <= "\u097F" for char in text)

    def retrieve_and_rerank(
        self,
        claim_text: str,
        claim_time: Optional[datetime] = None,
        domain: Optional[str] = None
    ) -> Tuple[List[Evidence], Dict[str, Any]]:
        """
        Executes two-stage dense retrieval and re-ranking for a claim.

        Returns:
            Tuple of:
              - List[Evidence]: Top re-ranked evidence items with calculated temporal decay.
              - metadata: Dict with S_max, is_evidence_void, and retrieval telemetry.
        """
        now = claim_time or datetime.now(timezone.utc)
        corpus = self.store.get_corpus()
        doc_embeddings = self.store.get_embeddings()

        if len(corpus) == 0 or doc_embeddings is None:
            logger.warning("Empty knowledge corpus.")
            return [], {"max_similarity": 0.0, "is_evidence_void": True}

        is_indic = self._is_devanagari(claim_text)

        # Encode query using the unified multilingual encoder
        query_emb = self.encoder.encode([claim_text], normalize_embeddings=True)
        query_vec = np.asarray(query_emb[0], dtype=np.float32)

        # 2. Stage 1: Dense Cosine Similarity Search
        # All embeddings are normalized, so cosine similarity is dot product
        similarities = np.dot(doc_embeddings, query_vec)
        s_max = float(np.max(similarities)) if len(similarities) > 0 else 0.0

        # Check abstention condition: If highest similarity is below threshold, signal DATA_VOID
        is_evidence_void = s_max < self.abstention_threshold

        top_indices = np.argsort(similarities)[::-1][:self.dense_top_k]

        # 3. Stage 2: Multi-Factor Re-Ranking
        ranked_candidates = []
        for idx in top_indices:
            doc = corpus[idx]
            sim_dense = float(similarities[idx])

            # Lexical overlap score
            combined_doc_text = f"{doc.get('title', '')} {doc.get('snippet', '')}"
            sim_lex = compute_token_overlap(claim_text, combined_doc_text)

            # Publisher authority weight
            auth_weight = float(doc.get("publisher_authority", 0.85))

            # Temporal Credibility Decay
            pub_date_str = doc.get("publish_date")
            ev_date = None
            if pub_date_str:
                try:
                    ev_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                except Exception:
                    ev_date = None

            doc_domain = domain or doc.get("domain", "general")
            w_t = calculate_temporal_decay(
                claim_time=now,
                evidence_time=ev_date,
                domain=doc_domain
            )

            # Multi-factor composite ranking score:
            # Semantic relevance is primary; irrelevant candidates (dense < 0.20) are filtered out.
            if sim_dense < 0.20:
                relevance = 0.0
            else:
                relevance = 0.70 * sim_dense + 0.30 * sim_lex

            composite_score = relevance * (0.80 + 0.20 * auth_weight) * w_t

            evidence_item = Evidence(
                source_title=doc.get("title", "Verified Knowledge Base"),
                publisher=doc.get("publisher", "Accredited Fact Check Unit"),
                url=doc.get("url", ""),
                publish_date=ev_date or now,
                snippet=doc.get("snippet", ""),
                semantic_similarity=min(1.0, max(0.0, round(float(sim_dense), 4))),
                temporal_weight=min(1.0, max(0.0, round(float(w_t), 4))),
                final_score=min(1.0, max(0.0, round(float(composite_score), 4))),
                grounded_verdict=doc.get("grounded_verdict", None),
            )

            ranked_candidates.append({
                "evidence": evidence_item,
                "composite_score": composite_score,
                "grounded_verdict": doc.get("grounded_verdict", "VERIFIED")
            })

        # Sort by composite score
        ranked_candidates.sort(key=lambda x: x["composite_score"], reverse=True)
        top_ranked = ranked_candidates[:self.rerank_top_m]

        evidences = [item["evidence"] for item in top_ranked]
        primary_verdict = top_ranked[0]["grounded_verdict"] if top_ranked else "DATA_VOID"

        metadata = {
            "query_text": claim_text,
            "is_indic": is_indic,
            "max_dense_similarity": round(s_max, 4),
            "is_evidence_void": is_evidence_void,
            "abstention_threshold": self.abstention_threshold,
            "retrieved_count": len(evidences),
            "suggested_grounded_verdict": "DATA_VOID" if is_evidence_void else primary_verdict
        }

        return evidences, metadata


if __name__ == "__main__":
    retriever = TwoStageEvidenceRetriever()
    query = "COVID vaccines contain microchips and cause infertility"
    evs, meta = retriever.retrieve_and_rerank(query)
    print(f"Query: {query}")
    print(f"Max Sim: {meta['max_dense_similarity']}, Void: {meta['is_evidence_void']}, Verdict: {meta['suggested_grounded_verdict']}")
    for e in evs:
        print(f" - [{e.semantic_similarity:.2f}] {e.source_title} (Temporal w={e.temporal_weight:.2f})")
