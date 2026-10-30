"""TruthLens-Omni Application Launcher.

Usage:
    python run.py          # Starts the FastAPI HTTP microservice
    python run.py --demo   # Runs interactive terminal verification on sample claims
"""

import sys
import argparse
import uvicorn

# Ensure UTF-8 console output on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.core.config import settings
from src.core.types import VerificationRequest
from src.fusion.truthlens_engine import TruthLensEngine

def run_server():
    """Start the production FastAPI server."""
    print(f"\n=======================================================")
    print(f"  Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"  Docs available at: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"  Health check:     http://{settings.HOST}:{settings.PORT}/api/v1/health")
    print(f"=======================================================\n")
    uvicorn.run("src.api.server:app", host=settings.HOST, port=settings.PORT, reload=False)

def run_demo():
    """Execute live verification on sample claims demonstrating Neuro-Symbolic grounding."""
    print("\n[+] Initializing TruthLens-Omni Neuro-Symbolic Engine...\n")
    engine = TruthLensEngine()

    samples = [
        {
            "title": "Sample 1: Viral Microchip Conspiracy (Ground-Truth Refutation)",
            "text": "Viral social media posts claim COVID-19 vaccines contain secret microchips designed for human tracking.",
            "publisher": "dailyconspiracy.net",
        },
        {
            "title": "Sample 2: Satirical News Parody (The Onion Disentanglement)",
            "text": "NASA Announces Plans To Colonize Sun At Night To Avoid Burning Up.",
            "publisher": "theonion.com",
        },
        {
            "title": "Sample 3: Zero-Assumption Data-Void (Strict Non-Guessing)",
            "text": "Unverified rumor claims local municipal office closed early on Tuesday.",
            "publisher": "unregistered-unknown-source.xyz",
        },
    ]

    for item in samples:
        print(f"===========================================================")
        print(f"  {item['title']}")
        print(f"===========================================================")
        req = VerificationRequest(text=item["text"], publisher=item["publisher"])
        res = engine.verify(req)
        print(f"Verdict:        {res.verdict.value}")
        print(f"Confidence:     {res.confidence_score:.1%}")
        print(f"Latency:        {res.latency_ms:.1f} ms")
        print(f"\n[Explanation]:\n  {res.explanation}")

        if res.nutrition_card:
            card = res.nutrition_card
            print("\n[Contextual Nutrition Card (Feature 1)]:")
            print(f"  * Factual Grounding:       {card.factual_grounding_score:.1f} / 100")
            print(f"  * Source Transparency:     {card.source_transparency_score:.1f} / 100")
            print(f"  * Organic Diffusion:       {card.organic_diffusion_score:.1f} / 100")
            print(f"  * Rhetorical Clickbait:    {card.sensationalism_score:.1f} / 100")
            print(f"  * Temporal Freshness w(t): {card.temporal_freshness_score:.1f} / 100")

        print("\n[Sentence-Level Check-Worthiness Highlighting (Feature 2)]:")
        for c in res.claims:
            tag = "[REFUTED]" if c.highlight_status.value == "REFUTED" else ("[VERIFIED]" if c.highlight_status.value == "VERIFIED" else "[DATA_VOID]")
            citation_str = f" [Cited: {c.citation}]" if c.citation else ""
            print(f"  {tag} \"{c.text}\" (Worthiness: {c.check_worthiness:.2f}){citation_str}")

        print("\n[Deterministic Provenance Chain]:")
        for step in res.provenance_chain:
            print(f"  * {step}")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TruthLens-Omni Runner")
    parser.add_argument("--demo", action="store_true", help="Run interactive terminal demonstration")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    else:
        run_server()
