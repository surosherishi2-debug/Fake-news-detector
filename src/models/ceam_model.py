"""Context-Enhanced Attention Mechanism (CEAM) & Multimodal TruthLens Neural Architecture.

Derived from TruthLens (IEEE TNN 2024 / EDI.researchpaper.pdf):
Fuses Claim token embeddings, Evidence representations, Temporal Decay w(t) = exp(-lambda * delta_t),
and Heterogeneous Graph Transformer (HGT) social cascade embeddings via Gated Cross-Attention.
"""

import math
from typing import Optional, Tuple, Dict, Any
import torch
import torch.nn as nn
import torch.nn.functional as F

class CrossAttentionLayer(nn.Module):
    """
    Multi-Head Cross-Attention between Query (Claim) and Key/Value (Evidence).
    Applies temporal decay attenuation directly to attention logits:
    Attention(Q, K, V) = softmax((Q K^T / sqrt(d_k)) * exp(-lambda * delta_t)) V
    """

    def __init__(self, embed_dim: int = 128, num_heads: int = 4, dropout: float = 0.1):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        assert self.head_dim * num_heads == embed_dim, "embed_dim must be divisible by num_heads"

        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        temporal_weight: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            query: [Batch, SeqLen_Q, Dim] (Claim tokens)
            key: [Batch, SeqLen_K, Dim] (Evidence tokens)
            value: [Batch, SeqLen_V, Dim] (Evidence tokens)
            temporal_weight: Optional [Batch, 1, 1] decay multiplier w(t) in [0, 1]
        """
        batch_size = query.size(0)

        # Projections and multi-head split
        q = self.q_proj(query).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(key).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(value).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)

        # Scaled dot-product attention
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)

        # Apply temporal decay modulation if provided
        if temporal_weight is not None:
            # Reshape temporal weight to [Batch, 1, 1, 1] for broadcasting
            tw = temporal_weight.view(batch_size, 1, 1, 1)
            scores = scores * tw

        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)

        context = torch.matmul(attn_weights, v)
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.embed_dim)
        output = self.out_proj(context)

        return output, attn_weights

class MultimodalGatedFusion(nn.Module):
    """
    Gated Fusion mechanism combining textual cross-attended context with
    graph cascade embeddings from the Heterogeneous Graph Transformer (HGT).
    gate = sigmoid(W_g [h_text || h_graph])
    h_fused = gate * h_text + (1 - gate) * h_graph
    """

    def __init__(self, text_dim: int = 128, graph_dim: int = 64, hidden_dim: int = 128):
        super().__init__()
        self.proj_graph = nn.Linear(graph_dim, text_dim)
        self.gate_layer = nn.Sequential(
            nn.Linear(text_dim + text_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, text_dim),
            nn.Sigmoid()
        )
        self.layer_norm = nn.LayerNorm(text_dim)

    def forward(self, h_text: torch.Tensor, h_graph: torch.Tensor) -> torch.Tensor:
        """
        Args:
            h_text: [Batch, text_dim] pooled textual representation
            h_graph: [Batch, graph_dim] cascade representation from HGT
        """
        h_graph_proj = self.proj_graph(h_graph)
        concat = torch.cat([h_text, h_graph_proj], dim=-1)
        gate = self.gate_layer(concat)
        fused = gate * h_text + (1.0 - gate) * h_graph_proj
        return self.layer_norm(fused)

class CEAMTruthLensModel(nn.Module):
    """
    Full PyTorch implementation of the Context-Enhanced Attention TruthLens architecture.
    4 output classes: 0: REAL, 1: FAKE, 2: SATIRE, 3: DATA_VOID
    """

    def __init__(
        self,
        vocab_size: int = 10000,
        embed_dim: int = 128,
        graph_dim: int = 64,
        num_classes: int = 4,
        num_heads: int = 4,
        dropout: float = 0.1
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.token_embeddings = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        
        # Cross-Attention between Claim and Evidence
        self.cross_attention = CrossAttentionLayer(embed_dim=embed_dim, num_heads=num_heads, dropout=dropout)
        self.self_attention = nn.MultiheadAttention(embed_dim=embed_dim, num_heads=num_heads, batch_first=True)
        
        # Multimodal Gate
        self.fusion_gate = MultimodalGatedFusion(text_dim=embed_dim, graph_dim=graph_dim)
        
        # Epistemic Classification MLP Head
        self.classifier = nn.Sequential(
            nn.Linear(embed_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes)
        )

    def forward(
        self,
        claim_token_ids: torch.Tensor,
        evidence_token_ids: torch.Tensor,
        graph_cascade_emb: torch.Tensor,
        temporal_decay_weights: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            claim_token_ids: [Batch, L_claim] LongTensor
            evidence_token_ids: [Batch, L_evidence] LongTensor
            graph_cascade_emb: [Batch, graph_dim] FloatTensor
            temporal_decay_weights: [Batch, 1] FloatTensor (values in [0, 1])

        Returns:
            logits: [Batch, num_classes]
            attention_weights: [Batch, num_heads, L_claim, L_evidence]
        """
        claim_emb = self.token_embeddings(claim_token_ids)
        ev_emb = self.token_embeddings(evidence_token_ids)

        # 1. Cross-Attention with Temporal Weighting
        cross_out, attn_weights = self.cross_attention(
            query=claim_emb,
            key=ev_emb,
            value=ev_emb,
            temporal_weight=temporal_decay_weights
        )

        # 2. Mean Pooling across sequence dimension
        h_text = torch.mean(cross_out, dim=1)

        # 3. Multimodal Gated Fusion with HGT Graph Embedding
        h_fused = self.fusion_gate(h_text, graph_cascade_emb)

        # 4. Epistemic Classification Logits
        logits = self.classifier(h_fused)

        return logits, attn_weights

    @torch.no_grad()
    def predict_epistemic_state(
        self,
        claim_token_ids: torch.Tensor,
        evidence_token_ids: torch.Tensor,
        graph_cascade_emb: torch.Tensor,
        temporal_decay_weights: Optional[torch.Tensor] = None
    ) -> Dict[str, Any]:
        """Inference helper returning normalized probabilities and verdict label."""
        self.eval()
        logits, attn = self.forward(claim_token_ids, evidence_token_ids, graph_cascade_emb, temporal_decay_weights)
        probs = F.softmax(logits, dim=-1).squeeze(0).tolist()
        
        labels = ["REAL", "FAKE", "SATIRE", "DATA_VOID"]
        max_idx = int(torch.argmax(logits, dim=-1).item())
        
        return {
            "verdict": labels[max_idx],
            "confidence": probs[max_idx],
            "probabilities": {labels[i]: round(probs[i], 4) for i in range(len(labels))},
            "temporal_weight_applied": float(temporal_decay_weights.item()) if temporal_decay_weights is not None else 1.0
        }
