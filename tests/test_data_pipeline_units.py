"""Unit tests for deterministic DataPipeline utilities."""

import json
import os

from src.data.pipeline import (
    DataPipeline,
    ProcessedClaimSample,
    clean_text,
    compute_char_ngrams,
    jaccard_similarity,
)


def test_clean_text_normalization():
    # Empty and None handling
    assert clean_text("") == ""
    assert clean_text("   ") == ""

    # Whitespace and newline collapsing
    dirty = "This   is\r\na  \t\t\ntest   statement.   "
    assert clean_text(dirty) == "This is a test statement."

    # NFKC Unicode normalization
    unicode_sample = "COVID‐19 \u00a0vaccine"  # non-breaking hyphen and non-breaking space
    cleaned = clean_text(unicode_sample)
    assert "COVID" in cleaned
    assert " " in cleaned


def test_compute_char_ngrams():
    text = "Fake News"
    ngrams_4 = compute_char_ngrams(text, n=4)
    # text lowercased and stripped of space: 'fakenews' (len 8) -> 8 - 4 + 1 = 5 ngrams
    assert len(ngrams_4) == 5
    assert "fake" in ngrams_4
    assert "news" in ngrams_4

    # Short text < n
    short_ngrams = compute_char_ngrams("ab", n=4)
    assert short_ngrams == {"ab"}


def test_jaccard_similarity():
    set_a = {"fake", "news", "viral"}
    set_b = {"fake", "news", "report"}

    # Intersection = 2, Union = 4 -> J = 0.5
    j = jaccard_similarity(set_a, set_b)
    assert abs(j - 0.5) < 1e-4

    # Disjoint sets
    assert jaccard_similarity(set_a, {"completely", "different"}) == 0.0

    # Empty sets
    assert jaccard_similarity(set(), set_b) == 0.0
    assert jaccard_similarity(set_a, set()) == 0.0
    assert jaccard_similarity(set(), set()) == 0.0


def test_processed_claim_sample_schema():
    sample = ProcessedClaimSample(
        id="test-001",
        dataset="liar_plus",
        claim_text="The economy grew by five percent last quarter.",
        evidence_text="Commerce Department reports 5.0 percent annualized GDP growth.",
        raw_label="true",
        grounded_label="VERIFIED",
        domain="politics",
        language="en",
        publication_date="2023-01-01",
        metadata={"speaker": "Economist"},
    )
    assert sample.id == "test-001"
    assert sample.grounded_label == "VERIFIED"
    assert sample.domain == "politics"
    assert sample.metadata["speaker"] == "Economist"


def test_data_pipeline_save_splits(tmp_path):
    pipeline = DataPipeline(seed=42)
    sample = ProcessedClaimSample(
        id="s1",
        dataset="mock",
        claim_text="Sample claim.",
        raw_label="false",
        grounded_label="REFUTED",
        domain="health",
        language="en",
    )
    splits = {"train": [sample], "val": [sample], "test": [sample]}

    target_dir = str(tmp_path / "mock")
    pipeline.save_splits("mock", splits, output_dir=str(tmp_path))

    assert os.path.exists(os.path.join(target_dir, "train.jsonl"))
    assert os.path.exists(os.path.join(target_dir, "val.jsonl"))
    assert os.path.exists(os.path.join(target_dir, "test.jsonl"))

    with open(os.path.join(target_dir, "train.jsonl"), encoding="utf-8") as f:
        loaded = json.loads(f.readline())
        assert loaded["id"] == "s1"
        assert loaded["grounded_label"] == "REFUTED"
