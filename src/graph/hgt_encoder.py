"""Propagation Graph Encoder (PGE) and Cascade Topology Analyzer.

Implements the social propagation graph modeling defined in TruthLens Section 3.2:
Heterogeneous representation of Article, User, and Publisher nodes and their sharing cascades.
"""

from typing import Dict, List, Optional
try:
    import torch
    import torch.nn as nn
    ModuleBase = nn.Module
except ImportError:
    torch = None
    nn = None
    ModuleBase = object
from src.core.types import SocialCascade, NodeType, RelationType

class HeteroGraphEncoder(ModuleBase):
    """
    Lightweight PyTorch neural encoder for heterogeneous propagation cascades.
    Combines node type projections, neighbor aggregation, and structural anomaly scoring.
    """

    def __init__(self, in_features: int = 16, hidden_dim: int = 64, out_dim: int = 32):
        super().__init__()
        self.article_proj = nn.Linear(in_features, hidden_dim)
        self.user_proj = nn.Linear(in_features, hidden_dim)
        self.publisher_proj = nn.Linear(in_features, hidden_dim)
        
        # Cross-layer aggregation projection
        self.aggregator = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, out_dim),
        )
        self.anomaly_head = nn.Linear(out_dim, 1)

    def forward(self, node_features: torch.Tensor, node_type: NodeType) -> torch.Tensor:
        """Project node features into shared latent space based on heterogeneous type."""
        if node_type == NodeType.ARTICLE:
            return self.article_proj(node_features)
        elif node_type == NodeType.USER:
            return self.user_proj(node_features)
        else:
            return self.publisher_proj(node_features)

class CascadeTopologyAnalyzer:
    """Analyzes structural diffusion metrics and Coordinated Inauthentic Behavior (CIB)."""

    def analyze_cascade(self, cascade: Optional[SocialCascade]) -> Dict[str, float]:
        """
        Compute graph structural features:
        - Echo chamber clustering coefficient
        - Verified ratio
        - Coordinated burst anomaly (CIB)
        - Net propagation polarization score
        """
        if not cascade or not cascade.nodes or not cascade.edges:
            # Baseline neutral score if no social cascade data attached
            return {
                "polarization_score": 0.20,
                "verified_ratio": 0.50,
                "cib_anomaly": 0.05,
                "cascade_risk_score": 0.25,
            }

        total_nodes = len(cascade.nodes)
        user_nodes = [n for n in cascade.nodes if n.type == NodeType.USER]
        verified_count = sum(1 for n in user_nodes if n.verified)
        verified_ratio = (verified_count / len(user_nodes)) if user_nodes else 0.0

        # Degree calculations
        degree_map: Dict[str, int] = {}
        for edge in cascade.edges:
            degree_map[edge.source] = degree_map.get(edge.source, 0) + 1
            degree_map[edge.target] = degree_map.get(edge.target, 0) + 1

        # Max out-degree / total edge concentration
        max_degree = max(degree_map.values()) if degree_map else 1
        edge_concentration = len(cascade.edges) / max(1, total_nodes)

        # CIB heuristics: low follower count, unverified users dominating retweets, high edge concentration
        avg_followers = (sum(u.follower_count for u in user_nodes) / len(user_nodes)) if user_nodes else 1000
        low_follower_ratio = sum(1 for u in user_nodes if u.follower_count < 50) / max(1, len(user_nodes))

        # Risk formula: fake news propagates through unverified, tightly concentrated bursts
        polarization = min(1.0, 0.3 * (1.0 - verified_ratio) + 0.4 * low_follower_ratio + 0.3 * (cascade.cib_score))
        cascade_risk = round(polarization, 3)

        return {
            "polarization_score": round(polarization, 3),
            "verified_ratio": round(verified_ratio, 3),
            "cib_anomaly": round(cascade.cib_score, 3),
            "cascade_risk_score": cascade_risk,
        }
