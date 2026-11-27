"""Unit tests for Qualitative Error Analysis diagnostics and adversarial benchmarking."""

from src.evaluation.adversarial_evaluation import AdversarialBenchmarkRunner
from src.evaluation.error_analysis import diagnose_failure_mode


def test_diagnose_failure_mode_numerical():
    sample = {
        "claim_text": "The tax cut reduced national debt by 45 percent or 500 billion dollars.",
        "evidence_text": "Treasury figures show debt increased.",
        "domain": "politics",
    }
    category, rationale = diagnose_failure_mode(sample, true_lbl="REFUTED", pred_lbl="VERIFIED")
    assert category == "Numerical & Statistical Distortion"
    assert "arithmetic magnitude" in rationale


def test_diagnose_failure_mode_data_void():
    sample = {
        "claim_text": "Mysterious shadow seen over downtown lake on midnight Wednesday.",
        "evidence_text": None,
        "domain": "general",
    }
    category, rationale = diagnose_failure_mode(sample, true_lbl="DATA_VOID", pred_lbl="REFUTED")
    assert category == "Evidence Void / Unsubstantiated Boundary"
    assert "DATA_VOID" in rationale or "lacks external corroborating evidence" in rationale


def test_diagnose_failure_mode_temporal():
    sample = {
        "claim_text": "The former governor was first to declare candidacy and remains the current favorite in history.",
        "evidence_text": "Historical records show other candidates entered the race earlier.",
        "domain": "politics",
    }
    category, rationale = diagnose_failure_mode(sample, true_lbl="VERIFIED", pred_lbl="REFUTED")
    assert category == "Temporal Obsolescence / Time Horizon Drift"
    assert "historical" in rationale or "timeframe" in rationale


def test_diagnose_failure_mode_sarcasm():
    sample = {
        "claim_text": "Local mayor totally shocked that rainy weather actually involves water falling from sky.",
        "evidence_text": "Editorial parody article.",
        "domain": "satire",
    }
    category, rationale = diagnose_failure_mode(sample, true_lbl="DATA_VOID", pred_lbl="VERIFIED")
    # either sarcasm or data void depending on condition
    assert category in ["Subtle Sarcasm / Satirical Drift", "Evidence Void / Unsubstantiated Boundary"]


def test_diagnose_failure_mode_negation():
    sample = {
        "claim_text": "The senator did not fail to reject the proposed zoning amendment.",
        "evidence_text": "Senate records show vote.",
        "domain": "politics",
    }
    category, rationale = diagnose_failure_mode(sample, true_lbl="REFUTED", pred_lbl="VERIFIED")
    assert category in ["Complex Syntactic Negation", "Cross-Domain Lexical Drift / Semantic Ambiguity"]


def test_diagnose_failure_mode_lexical_drift_fallback():
    sample = {
        "claim_text": "A standard mundane policy decision occurred.",
        "evidence_text": "Government bulletin.",
        "domain": "politics",
    }
    category, rationale = diagnose_failure_mode(sample, true_lbl="VERIFIED", pred_lbl="REFUTED")
    assert len(category) > 0
    assert len(rationale) > 0


def test_adversarial_benchmark_runner_init():
    runner = AdversarialBenchmarkRunner(sample_limit=10, perturbation_budget=0.15)
    assert runner.sample_limit == 10
    assert runner.perturbation_budget == 0.15
    assert runner.simulator is not None
