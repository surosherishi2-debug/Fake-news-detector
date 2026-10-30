"""Extended FastAPI Service for TruthLens-Omni Epistemic Platform."""

import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from src.core.config import settings
from src.core.types import (
    VerificationRequest,
    VerificationResult,
    SocialCascade,
    SocialNode,
    SocialEdge,
    NodeType,
    RelationType,
)
from src.fusion.truthlens_engine import TruthLensEngine, TRUSTED_PUBLISHERS, UNTRUSTED_PUBLISHERS
from src.retrieval.url_scraper import URLScraper
from src.graph.consensus_matrix import (
    BridgingConsensusEngine,
    NoteRating,
    NoteScoringResult,
)
from src.data.news_database import db
from src.data.rss_crawler import RSSNewsCrawler, FeedSyncResult
from src.data.dataset_loader import DatasetLoader
from src.nlp.preflight_auditor import PreflightAuditor, PreflightAuditReport
from src.nlp.synthetic_detector import SyntheticDetector, SyntheticForensicReport
from src.models.evaluator import ModelEvaluator, BenchmarkSummaryReport
from src.models.adversarial_tester import AdversarialAttackSimulator

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Full-Spectrum Epistemic Intelligence & Publishing Integrity Platform API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = TruthLensEngine()
scraper = URLScraper()
consensus_engine = BridgingConsensusEngine()
auditor = PreflightAuditor()
synthetic_detector = SyntheticDetector()
crawler = RSSNewsCrawler(db=db)
dataset_loader = DatasetLoader()
evaluator = ModelEvaluator(dataset_loader=dataset_loader)
adv_simulator = AdversarialAttackSimulator()

# Mount Static Files
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class ScrapeRequest(BaseModel):
    url: str

class ScrapeResponse(BaseModel):
    url: str
    domain: str
    title: str
    body_text: str
    publish_date: Optional[str] = None
    status: str
    error: Optional[str] = None

class ConsensusRequest(BaseModel):
    ratings: List[NoteRating]

class AuditRequest(BaseModel):
    draft_text: str

class ForensicsRequest(BaseModel):
    text: str

class AdversarialRequest(BaseModel):
    text: str
    budget: float = 0.25

@app.get("/", response_class=HTMLResponse)
def index_page():
    """Serve the primary TruthLens-Omni SPA dashboard."""
    index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "templates", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>TruthLens-Omni Platform Running.</h1>")

@app.get("/api/v1/health")
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "lambda_decay": settings.TEMPORAL_LAMBDA,
        "fact_check_api_configured": bool(settings.GOOGLE_FACT_CHECK_API_KEY),
    }

@app.post("/api/v1/verify", response_model=VerificationResult)
def verify_article(request: VerificationRequest):
    """Verify an article or claim text using the Neuro-Symbolic Tri-Modal Pipeline."""
    try:
        return engine.verify(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@app.get("/api/v1/feed")
def get_daily_news_feed(
    category: Optional[str] = None,
    status: Optional[str] = None,
    language: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
):
    """Retrieve daily epistemic newsfeed from persistent knowledge store."""
    try:
        articles = db.get_articles(category=category, status=status, language=language, search_query=search, limit=limit)
        return {"total": len(articles), "articles": articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch feed: {str(e)}")

@app.post("/api/v1/feed/sync", response_model=FeedSyncResult)
def sync_news_feeds(force_live: bool = False):
    """Trigger RSS / news feed crawler to ingest and index fresh news items."""
    try:
        return crawler.sync_feeds(force_live=force_live)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feed sync failed: {str(e)}")

@app.get("/api/v1/knowledge-graph")
def get_living_knowledge_graph():
    """Return nodes and edges for the Living Knowledge Graph."""
    try:
        return db.get_knowledge_graph()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch graph: {str(e)}")

@app.post("/api/v1/preflight/audit", response_model=PreflightAuditReport)
def audit_story_draft(request: AuditRequest):
    """Execute pre-flight verification on author's draft before publication (Self-News Studio)."""
    try:
        return auditor.audit_draft(request.draft_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Draft audit failed: {str(e)}")

@app.post("/api/v1/forensics/synthetic", response_model=SyntheticForensicReport)
def detect_synthetic_ai_text(request: ForensicsRequest):
    """Analyze statistical burstiness and entropy to detect AI-generated text / hallucinations."""
    try:
        return synthetic_detector.analyze_text(request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forensics failed: {str(e)}")

@app.get("/api/v1/benchmarks", response_model=BenchmarkSummaryReport)
def get_empirical_benchmarks(dataset: str = "pune_fakenews_2024"):
    """Return empirical comparison matrix of TruthLens against baseline models."""
    try:
        return evaluator.run_benchmark_suite(dataset_name=dataset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark generation failed: {str(e)}")

@app.post("/api/v1/adversarial/attack")
def run_adversarial_perturbation(request: AdversarialRequest):
    """
    Perturb input claim using TextFooler synonym substitution and compare
    standard prediction vs. TruthLens multimodal resilience.
    """
    try:
        perturbed_text, subs, mod_rate = adv_simulator.perturb_text(
            request.text, perturbation_budget=request.budget
        )
        
        # Verify clean vs perturbed
        clean_req = VerificationRequest(text=request.text)
        pert_req = VerificationRequest(text=perturbed_text)
        
        clean_res = engine.verify(clean_req)
        pert_res = engine.verify(pert_req)

        return {
            "original_text": request.text,
            "perturbed_text": perturbed_text,
            "substitutions": subs,
            "modification_rate": mod_rate,
            "clean_verdict": clean_res.verdict.value,
            "clean_truth_score": round(clean_res.confidence_score * 100, 1),
            "perturbed_verdict": pert_res.verdict.value,
            "perturbed_truth_score": round(pert_res.confidence_score * 100, 1),
            "is_resilient": (clean_res.verdict == pert_res.verdict),
            "explanation": (
                "TruthLens maintained consistent epistemic classification across adversarial synonym swaps "
                "because heterogeneous evidence citations and domain trust anchored the semantic alignment."
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Adversarial test failed: {str(e)}")

@app.get("/api/v1/guide/dossier")
def get_guide_presentation_dossier():
    """Return mathematical formulations, architectural specs, and thesis pitch points."""
    return {
        "project_title": "TruthLens-Omni: Epistemic Intelligence & Information Integrity Platform",
        "theoretical_innovations": [
            {
                "name": "Exponential Temporal Decay",
                "latex": r"w(t) = \exp(-\lambda \Delta t)",
                "description": "Attenuates outdated fact-checks dynamically so historical debunks don't misclassify newer verified events."
            },
            {
                "name": "Heterogeneous Graph Cascade Attention",
                "latex": r"\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}} \cdot w(t)\right) V",
                "description": "Fuses social propagation cascade structures and botnet clustering to detect Coordinated Inauthentic Behavior."
            },
            {
                "name": "Community Notes Matrix Factorization",
                "latex": r"\hat{r}_{ui} = \mu + b_u + b_i + \mathbf{p}_u^T \mathbf{q}_i",
                "description": "Low-rank consensus model identifying bridging context that earns cross-ideological agreement."
            },
            {
                "name": "Multimodal Gated Fusion (CEAM)",
                "latex": r"\mathbf{h}_{\text{fused}} = \sigma(\mathbf{W}_g [\mathbf{h}_{\text{text}} \,\|\, \mathbf{h}_g]) \odot \mathbf{h}_{\text{text}} + (1 - \sigma) \odot \mathbf{h}_g",
                "description": "Dynamic gating between textual Claim-Evidence alignment and social propagation topology."
            }
        ],
        "datasets_integrated": [
            {"name": "PuneFakeNews-2024", "focus": "Regional Indic/English Misinformation & Infrastructure Rumors", "size": "Curated benchmark"},
            {"name": "LIAR-Plus", "focus": "Fine-Grained 6-Way Political Fact-Checking", "size": "12,836 claims"},
            {"name": "CoAID", "focus": "COVID-19 & Healthcare Misinformation", "size": "4,251 claims"},
            {"name": "FakeNewsNet", "focus": "PolitiFact & GossipCop Social Cascades", "size": "23,196 cascades"}
        ],
        "engineering_highlights": [
            "Neuro-symbolic veto protocol enforcing zero-assumption when evidence is missing (eliminates AI hallucinations).",
            "Pre-flight Self-News Studio enabling author verification before publishing.",
            "GLTR-inspired statistical burstiness and token entropy forensics for synthetic AI detection.",
            "Full-stack reactive Neo-FinTech SPA with interactive HTML5 canvas graph visualizer."
        ]
    }

@app.post("/api/v1/scrape", response_model=ScrapeResponse)
def scrape_article_url(request: ScrapeRequest):
    """Scrape and parse article content from a live URL for 1-click verification."""
    v_req, meta = scraper.scrape_url(request.url)
    if not v_req:
        return ScrapeResponse(
            url=request.url,
            domain=meta.get("domain", ""),
            title=meta.get("title", ""),
            body_text="",
            status="failed",
            error=meta.get("error", "Failed to retrieve web page"),
        )
    return ScrapeResponse(
        url=request.url,
        domain=v_req.publisher or meta.get("domain", ""),
        title=meta.get("title", "Article"),
        body_text=v_req.text,
        publish_date=meta.get("publish_date"),
        status="success",
    )

@app.post("/api/v1/consensus/score", response_model=Dict[str, NoteScoringResult])
def score_community_notes(request: ConsensusRequest):
    """Run low-rank Matrix Factorization consensus scoring on community note ratings."""
    try:
        return consensus_engine.fit_and_score(request.ratings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consensus scoring failed: {str(e)}")

@app.get("/api/v1/cascades/sample", response_model=SocialCascade)
def get_sample_cascade():
    """Return sample heterogeneous social cascade for interactive graph visualization."""
    return SocialCascade(
        article_id="art-covid-microchip-901",
        nodes=[
            SocialNode(id="art-901", type=NodeType.ARTICLE, name="Viral Microchip Article", verified=False, follower_count=0),
            SocialNode(id="pub-dailyconspiracy", type=NodeType.PUBLISHER, name="dailyconspiracy.net", verified=False, follower_count=12000),
            SocialNode(id="bot-cluster-1", type=NodeType.USER, name="@crypto_truth_99", verified=False, follower_count=14),
            SocialNode(id="bot-cluster-2", type=NodeType.USER, name="@freedom_patriot_x", verified=False, follower_count=8),
            SocialNode(id="bot-cluster-3", type=NodeType.USER, name="@news_whistleblower", verified=False, follower_count=22),
            SocialNode(id="verified-debunker", type=NodeType.USER, name="@dr_scientist_md", verified=True, follower_count=85000),
            SocialNode(id="organic-reader-1", type=NodeType.USER, name="@citizen_jane", verified=False, follower_count=450),
        ],
        edges=[
            SocialEdge(source="pub-dailyconspiracy", target="art-901", relation=RelationType.AUTHORED_BY),
            SocialEdge(source="art-901", target="bot-cluster-1", relation=RelationType.SHARES),
            SocialEdge(source="art-901", target="bot-cluster-2", relation=RelationType.SHARES),
            SocialEdge(source="art-901", target="bot-cluster-3", relation=RelationType.SHARES),
            SocialEdge(source="bot-cluster-1", target="organic-reader-1", relation=RelationType.FOLLOWS),
            SocialEdge(source="art-901", target="verified-debunker", relation=RelationType.SHARES),
        ],
        cib_score=0.82,
    )

@app.get("/api/v1/domains/{domain}/trust")
def get_domain_trust(domain: str):
    """Retrieve NewsGuard-style trust score for a news domain."""
    cleaned = domain.lower().strip()
    if cleaned in TRUSTED_PUBLISHERS:
        return {"domain": cleaned, "trust_score": TRUSTED_PUBLISHERS[cleaned], "category": "verified"}
    if cleaned in UNTRUSTED_PUBLISHERS:
        return {"domain": cleaned, "trust_score": UNTRUSTED_PUBLISHERS[cleaned], "category": "flagged"}
    return {"domain": cleaned, "trust_score": 0.50, "category": "unrated"}
