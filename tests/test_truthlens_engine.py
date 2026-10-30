"""Unit tests for Neuro-Symbolic TruthLens-Omni Platform."""

from src.core.types import VerificationRequest, VerificationVerdict, HighlightStatus
from src.fusion.truthlens_engine import TruthLensEngine
from src.api.server import (
    health_check,
    get_domain_trust,
    verify_article,
    scrape_article_url,
    score_community_notes,
    get_sample_cascade,
    get_daily_news_feed,
    get_living_knowledge_graph,
    audit_story_draft,
    detect_synthetic_ai_text,
    ScrapeRequest,
    ConsensusRequest,
    AuditRequest,
    ForensicsRequest,
)
from src.graph.consensus_matrix import NoteRating
from src.data.news_database import db
from src.nlp.preflight_auditor import PreflightAuditor
from src.nlp.synthetic_detector import SyntheticDetector

def test_truthlens_engine_fake_claim_with_nutrition_card():
    engine = TruthLensEngine()
    req = VerificationRequest(
        text="Viral claim: COVID-19 vaccines contain microchips designed for human tracking.",
        publisher="dailyconspiracy.net",
    )
    result = engine.verify(req)
    assert result.verdict == VerificationVerdict.FAKE
    assert result.confidence_score >= 0.50
    assert len(result.claims) >= 1
    assert result.nutrition_card is not None
    assert result.nutrition_card.factual_grounding_score <= 50.0
    assert result.claims[0].highlight_status == HighlightStatus.REFUTED
    assert "Reuters" in result.claims[0].citation or "WHO" in result.claims[0].citation

def test_truthlens_engine_satire_disentanglement():
    engine = TruthLensEngine()
    req = VerificationRequest(
        text="NASA Announces Plans To Colonize Sun At Night To Avoid Burning Up.",
        publisher="theonion.com",
    )
    result = engine.verify(req)
    assert "Satirical Parody" in result.explanation
    assert result.nutrition_card is not None

def test_truthlens_engine_zero_assumption_data_void():
    """System must strictly refuse to guess when zero accredited evidence exists."""
    engine = TruthLensEngine()
    req = VerificationRequest(
        text="Unconfirmed rumor claims local municipal office closed early on Tuesday.",
        publisher="unregistered-unknown-source.xyz",
    )
    result = engine.verify(req)
    assert result.verdict == VerificationVerdict.UNCERTAIN
    assert "Data-Void" in result.explanation

def test_database_persistence_and_seed():
    """Verify database contains persistent multi-domain articles and entity graph."""
    articles = db.get_articles(limit=10)
    assert len(articles) >= 5
    assert any(a["status"] == "REAL" for a in articles)
    assert any(a["status"] == "FAKE" for a in articles)
    assert any(a["status"] == "SATIRE" for a in articles)

    graph = db.get_knowledge_graph()
    assert len(graph["nodes"]) >= 5
    assert len(graph["edges"]) >= 3

def test_preflight_auditor():
    """Test Self-News Studio authoring auditor."""
    auditor = PreflightAuditor()
    draft = (
        "Researchers at ISRO confirmed water ice near the south pole. "
        "Shocking reports claim COVID vaccines contain microchips for surveillance!"
    )
    report = auditor.audit_draft(draft)
    assert report.total_assertions >= 2
    assert report.unsupported_high_risk_count >= 1
    assert report.audit_readiness_score < 100.0
    assert len(report.recommendations) >= 1

def test_synthetic_detector():
    """Test AI Hallucination & Synthetic Text Forensics."""
    detector = SyntheticDetector()
    
    # Synthetic style text with low burstiness and signature transitions
    synthetic_sample = (
        "In today's digital age, it is crucial to note that quantum computing plays a pivotal role. "
        "Furthermore, navigating the complexities of artificial intelligence stands as a testament to human innovation. "
        "Moreover, it is important to remember that ethical considerations serve as a beacon of hope."
    )
    report_synth = detector.analyze_text(synthetic_sample)
    assert report_synth.ai_generated_probability >= 0.50
    assert report_synth.llm_signature_count >= 2

    # Natural human text with dynamic burstiness
    human_sample = (
        "Stop. Look at this number. According to the federal filings released at 3 PM yesterday, the company lost 14 million dollars. "
        "Nobody expected it. The market reacted instantly, driving prices down by twenty percent in six minutes flat."
    )
    report_human = detector.analyze_text(human_sample)
    assert report_human.burstiness_score > 4.0
    assert report_human.classification in ["HUMAN_AUTHORED", "HYBRID_HUMAN_EDITED"]

def test_api_endpoints():
    # 1. Health check
    res_health = health_check()
    assert res_health["status"] == "healthy"

    # 2. Domain trust check
    res_trust = get_domain_trust("reuters.com")
    assert res_trust["trust_score"] >= 0.90
    assert res_trust["category"] == "verified"

    # 3. Verification endpoint
    res_verify = verify_article(
        VerificationRequest(
            text="Scientists at ISRO confirmed lunar water and mineral ice near the south pole.",
            publisher="pib.gov.in",
        )
    )
    assert res_verify.verdict is not None
    assert res_verify.confidence_score > 0
    assert res_verify.nutrition_card is not None

    # 4. Feed & Knowledge Graph endpoints
    feed = get_daily_news_feed(limit=5)
    assert feed["total"] >= 1

    kg = get_living_knowledge_graph()
    assert len(kg["nodes"]) >= 1

    # 5. Preflight audit endpoint
    audit = audit_story_draft(AuditRequest(draft_text="Breaking unverified claim about election."))
    assert audit.audit_readiness_score > 0

    # 6. Forensics endpoint
    forensics = detect_synthetic_ai_text(ForensicsRequest(text="It is crucial to note that technology evolves."))
    assert forensics.ai_generated_probability >= 0.0

    # 7. Benchmarks & Guide Dossier endpoints
    from src.api.server import get_empirical_benchmarks, get_guide_presentation_dossier, run_adversarial_perturbation, AdversarialRequest
    bench = get_empirical_benchmarks("pune_fakenews_2024")
    assert len(bench.models) >= 4

    dossier = get_guide_presentation_dossier()
    assert len(dossier["theoretical_innovations"]) == 4
    assert len(dossier["datasets_integrated"]) == 4

    # 8. Adversarial endpoint
    adv_res = run_adversarial_perturbation(AdversarialRequest(text="The FDA approved the safe medicine in trials.", budget=0.30))
    assert "perturbed_text" in adv_res
    assert "clean_verdict" in adv_res

    # 9. Preflight Publish to Daily Feed & Knowledge Graph
    from src.api.server import publish_story_draft, PublishDraftRequest, get_entity_subgraph, export_guide_dossier_markdown
    pub_res = publish_story_draft(PublishDraftRequest(
        title="Student Grounded Investigation: Local Clean Energy Microgrid",
        content="Engineers validated 100kW rooftop solar microgrid deployment.",
        category="Climate",
        assertions=[{"text": "Rooftop solar microgrid generated 100kW power.", "is_supported": True}]
    ))
    assert pub_res["success"] is True
    assert "article_id" in pub_res

    # 10. Entity Details Subgraph
    ent_sub = get_entity_subgraph("ent-isro")
    assert ent_sub["name"] == "ISRO"
    assert "connections" in ent_sub

    # 11. Markdown Dossier Export
    md_dossier = export_guide_dossier_markdown()
    assert "# TruthLens-Omni" in md_dossier
    assert "Temporal Decay" in md_dossier
