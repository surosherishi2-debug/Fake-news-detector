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
            "category_label": "1. Fake / Disinformation (Biomedical Conspiracy)",
            "text": "Viral social media posts claim COVID-19 vaccines contain secret microchips designed for human tracking.",
            "publisher": "dailyconspiracy.net",
        },
        {
            "category_label": "2. True / Verified Claim (Public Health Consensus)",
            "text": "The FDA officially approved the updated vaccine booster formulation confirming clinical safety and efficacy.",
            "publisher": "fda.gov",
        },
        {
            "category_label": "3. Satirical News Parody (The Onion Disentanglement)",
            "text": "NASA Launches Giant Mirror Into Orbit So Earth Can Check Its Hair.",
            "publisher": "theonion.com",
        },
        {
            "category_label": "4. Zero-Assumption Data-Void (Strict Non-Guessing Abstention)",
            "text": "Anonymous unverified rumor claims city municipal commissioner secretly purchased three purple bicycles on Tuesday.",
            "publisher": "unregistered-unknown-source.xyz",
        },
        {
            "category_label": "5. Paraphrased Adversarial Claim (TextFooler Synonym Attack)",
            "text": "Food and Drug Administration endorsed the certified immunization formulation confirming it is unhazardous and potent.",
            "publisher": "medical-bulletin.org",
        },
        {
            "category_label": "6. Indic Regional Debunk (Marathi/Hindi IFCN Verification)",
            "text": "पुण्यात लष्कर तैनात करून संपूर्ण संचारबंदी लागू केल्याचा दावा सोशल मीडियावर व्हायरल होत आहे.",
            "publisher": "whatsapp-forward-archive.org",
        },
    ]

    for item in samples:
        print(f"===========================================================")
        print(f"  {item['category_label']}")
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
            print(f"  * Factual Grounding:                 {card.factual_grounding_score:.1f} / 100")
            print(f"  * Source Transparency:               {card.source_transparency_score:.1f} / 100")
            print(f"  * Organic Diffusion [SIMULATED]:     {card.organic_diffusion_score:.1f} / 100")
            print(f"  * Rhetorical Clickbait:              {card.sensationalism_score:.1f} / 100")
            print(f"  * Temporal Freshness w(t):           {card.temporal_freshness_score:.1f} / 100")

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
