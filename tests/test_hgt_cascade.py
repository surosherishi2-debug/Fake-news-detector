"""Unit tests for Propagation Graph Encoder (PGE) and cascade analysis."""

import torch
from src.core.types import SocialCascade, SocialNode, SocialEdge, NodeType, RelationType
from src.graph.hgt_encoder import HeteroGraphEncoder, CascadeTopologyAnalyzer

def test_hetero_graph_encoder_forward():
    encoder = HeteroGraphEncoder(in_features=8, hidden_dim=16, out_dim=8)
    features = torch.randn(2, 8)
    
    art_out = encoder(features, NodeType.ARTICLE)
    user_out = encoder(features, NodeType.USER)
    pub_out = encoder(features, NodeType.PUBLISHER)
    
    assert art_out.shape == (2, 16)
    assert user_out.shape == (2, 16)
    assert pub_out.shape == (2, 16)

def test_cascade_topology_normal_diffusion():
    analyzer = CascadeTopologyAnalyzer()
    cascade = SocialCascade(
        article_id="art-1",
        nodes=[
            SocialNode(id="u1", type=NodeType.USER, verified=True, follower_count=50000),
            SocialNode(id="u2", type=NodeType.USER, verified=True, follower_count=20000),
            SocialNode(id="u3", type=NodeType.USER, verified=False, follower_count=1200),
        ],
        edges=[
            SocialEdge(source="art-1", target="u1", relation=RelationType.SHARES),
            SocialEdge(source="u1", target="u2", relation=RelationType.SHARES),
            SocialEdge(source="u2", target="u3", relation=RelationType.SHARES),
        ],
        cib_score=0.02,
    )
    metrics = analyzer.analyze_cascade(cascade)
    assert metrics["verified_ratio"] > 0.50
    assert metrics["cascade_risk_score"] < 0.40

def test_cascade_topology_botnet_cluster():
    analyzer = CascadeTopologyAnalyzer()
    # Coordinated botnet: 0 verified users, very low followers, high CIB
    cascade = SocialCascade(
        article_id="art-fake-1",
        nodes=[
            SocialNode(id="bot1", type=NodeType.USER, verified=False, follower_count=5),
            SocialNode(id="bot2", type=NodeType.USER, verified=False, follower_count=12),
            SocialNode(id="bot3", type=NodeType.USER, verified=False, follower_count=8),
        ],
        edges=[
            SocialEdge(source="art-fake-1", target="bot1", relation=RelationType.SHARES),
            SocialEdge(source="art-fake-1", target="bot2", relation=RelationType.SHARES),
            SocialEdge(source="art-fake-1", target="bot3", relation=RelationType.SHARES),
        ],
        cib_score=0.85,
    )
    metrics = analyzer.analyze_cascade(cascade)
    assert metrics["verified_ratio"] == 0.0
    assert metrics["cascade_risk_score"] > 0.60
