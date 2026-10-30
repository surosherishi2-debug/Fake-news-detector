"""Core configuration and settings for TruthLens-Omni (FakeX)."""

from typing import Optional
import os

class Settings:
    """TruthLens-Omni engine settings."""
    PROJECT_NAME: str = "TruthLens-Omni"
    VERSION: str = "1.0.0"
    
    # Mathematical hyperparameter from TruthLens paper (Section 3.3)
    # Exponential decay rate for temporal evidence obsolescence: w(t) = exp(-λ * Δt)
    TEMPORAL_LAMBDA: float = float(os.getenv("TEMPORAL_LAMBDA", "0.1"))
    
    # Retrieval limits
    MAX_EVIDENCE_SENTENCES: int = int(os.getenv("MAX_EVIDENCE_SENTENCES", "5"))
    MIN_CLAIM_CONFIDENCE: float = float(os.getenv("MIN_CLAIM_CONFIDENCE", "0.6"))
    
    # External API keys
    GOOGLE_FACT_CHECK_API_KEY: Optional[str] = os.getenv("GOOGLE_FACT_CHECK_API_KEY", None)
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY", None)
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

settings = Settings()
