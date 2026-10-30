"""TruthLens-Omni Application Launcher.

Usage:
    python run.py          # Starts the FastAPI HTTP microservice
    python run.py --demo   # Runs interactive terminal verification on sample claims
"""

import sys
import argparse
import uvicorn
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
    """Execute live verification on sample claims."""
    print("\n[+] Initializing TruthLens-Omni Tri-Modal Engine...\n")
    engine = TruthLensEngine()

    samples = [
        {
            "title": "Sample 1: Viral Microchip Conspiracy (Fake News)",
            "text": "Viral social media posts claim COVID-19 vaccines contain secret microchips designed for human tracking.",
            "publisher": "dailyconspiracy.net",
        },
        {
            "title": "Sample 2: Space Exploration Milestone (Real News)",
            "text": "Scientists at ISRO confirmed that the Pragyan rover analyzed lunar soil and detected sulfur near the lunar south pole.",
            "publisher": "pib.gov.in",
        },
        {
            "title": "Sample 3: Breaking Unconfirmed Event (Uncertain / Pending Consensus)",
            "text": "Breaking reports suggest sudden unverified market fluctuations in private equity transactions.",
            "publisher": "randomblog123.org",
        },
    ]

    for item in samples:
        print(f"--- {item['title']} ---")
        req = VerificationRequest(text=item["text"], publisher=item["publisher"])
        res = engine.verify(req)
        print(f"Verdict:        {res.verdict.value}")
        print(f"Confidence:     {res.confidence_score:.1%}")
        print(f"Latency:        {res.latency_ms:.1f} ms")
        print(f"Explanation:    {res.explanation}")
        print("Provenance Chain:")
        for step in res.provenance_chain:
            print(f"  • {step}")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TruthLens-Omni Runner")
    parser.add_argument("--demo", action="store_true", help="Run interactive terminal demonstration")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    else:
        run_server()
