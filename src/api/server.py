"""FastAPI Service for TruthLens-Omni Real-Time Verification."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.core.types import VerificationRequest, VerificationResult
from src.fusion.truthlens_engine import TruthLensEngine, TRUSTED_PUBLISHERS, UNTRUSTED_PUBLISHERS

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Real-Time Multimodal Misinformation Intelligence & Consensus Engine API",
)

# Enable CORS for browser extension and Next.js dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = TruthLensEngine()

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs": "/docs",
    }

@app.get("/api/v1/health")
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "lambda_decay": settings.TEMPORAL_LAMBDA,
        "fact_check_api_configured": bool(settings.GOOGLE_FACT_CHECK_API_KEY),
    }

@app.post("/api/v1/verify", response_model=VerificationResult)
def verify_article(request: VerificationRequest):
    """
    Verify an article or claim text using the TruthLens Tri-Modal Pipeline.
    Evaluates:
    - Claim Decomposition
    - Claim-Evidence Alignment Module (CEAM) with temporal decay w(t)
    - Propagation Graph Encoder (PGE) cascade risk
    - Publisher credibility history
    """
    try:
        return engine.verify(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@app.get("/api/v1/domains/{domain}/trust")
def get_domain_trust(domain: str):
    """Retrieve NewsGuard-style trust score for a news domain."""
    cleaned = domain.lower().strip()
    if cleaned in TRUSTED_PUBLISHERS:
        return {"domain": cleaned, "trust_score": TRUSTED_PUBLISHERS[cleaned], "category": "verified"}
    if cleaned in UNTRUSTED_PUBLISHERS:
        return {"domain": cleaned, "trust_score": UNTRUSTED_PUBLISHERS[cleaned], "category": "flagged"}
    return {"domain": cleaned, "trust_score": 0.50, "category": "unrated"}
