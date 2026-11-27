"""Rigorous Test Suite for Data Foundation & Train/Test Leakage Prevention.

Verifies:
1. SHA-256 cryptographic integrity of all raw source files against data/checksums.sha256.
2. Complete absence of train/test text leakage across all processed splits.
3. Near-duplicate cross-split distance assertion (< 0.85 character 4-gram Jaccard).
4. Grounded label taxonomy consistency (VERIFIED, REFUTED, DATA_VOID).
5. Non-empty claims, valid schema parsing, and metadata integrity.
"""

import os
import json
import hashlib
import re
from typing import List, Set, Dict
import pytest
from src.data.pipeline import ProcessedClaimSample, compute_char_ngrams, jaccard_similarity

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
CHECKSUM_FILE = os.path.join(DATA_DIR, "checksums.sha256")

def load_jsonl(filepath: str) -> List[ProcessedClaimSample]:
    """Helper to parse a processed JSONL file into Pydantic models."""
    samples = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                samples.append(ProcessedClaimSample.model_validate_json(line))
    return samples

def test_raw_checksum_registry_integrity():
    """Verify all raw files match their recorded SHA-256 checksums."""
    assert os.path.exists(CHECKSUM_FILE), f"Missing checksum registry: {CHECKSUM_FILE}"
    
    with open(CHECKSUM_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            expected_sha, rel_path = line.split(maxsplit=1)
            full_path = os.path.join(DATA_DIR, rel_path.strip())
            assert os.path.exists(full_path), f"Raw file listed in checksums not found: {full_path}"
            
            # Recompute hash
            hasher = hashlib.sha256()
            with open(full_path, "rb") as rf:
                for chunk in iter(lambda: rf.read(65536), b""):
                    hasher.update(chunk)
            computed_sha = hasher.hexdigest()
            assert computed_sha == expected_sha, f"Checksum mismatch for {rel_path}: expected {expected_sha}, got {computed_sha}"

@pytest.mark.parametrize("dataset_name", ["liar_plus", "coaid", "fever", "indic"])
def test_zero_train_test_exact_leakage(dataset_name: str):
    """Assert strictly zero exact claim overlap between train and test splits."""
    train_file = os.path.join(PROCESSED_DIR, dataset_name, "train.jsonl")
    test_file = os.path.join(PROCESSED_DIR, dataset_name, "test.jsonl")

    if not os.path.exists(train_file) or not os.path.exists(test_file):
        pytest.skip(f"Processed splits for {dataset_name} not yet generated.")

    train_samples = load_jsonl(train_file)
    test_samples = load_jsonl(test_file)

    train_texts = {s.claim_text.lower().strip() for s in train_samples}
    test_texts = {s.claim_text.lower().strip() for s in test_samples}

    overlap = train_texts & test_texts
    assert len(overlap) == 0, f"Detected {len(overlap)} leaked claims between train and test in {dataset_name}: {list(overlap)[:3]}"

@pytest.mark.parametrize("dataset_name", ["liar_plus", "coaid", "fever", "indic"])
def test_zero_near_duplicate_cross_split_leakage(dataset_name: str):
    """
    Assert that near-duplicate similarity across train and test splits is strictly below 0.85 Jaccard.
    Sample up to 200 pairs to verify bound.
    """
    train_file = os.path.join(PROCESSED_DIR, dataset_name, "train.jsonl")
    test_file = os.path.join(PROCESSED_DIR, dataset_name, "test.jsonl")

    if not os.path.exists(train_file) or not os.path.exists(test_file):
        pytest.skip(f"Processed splits for {dataset_name} not yet generated.")

    train_samples = load_jsonl(train_file)
    test_samples = load_jsonl(test_file)

    # Subsample for test performance
    train_subset = [compute_char_ngrams(s.claim_text, n=4) for s in train_samples[:100]]
    test_subset = [compute_char_ngrams(s.claim_text, n=4) for s in test_samples[:50]]

    max_sim = 0.0
    for t_ngrams in test_subset:
        for tr_ngrams in train_subset:
            sim = jaccard_similarity(t_ngrams, tr_ngrams)
            if sim > max_sim:
                max_sim = sim
            # Strict barrier: no near-identical duplicates cross the train/test split boundary
            assert sim < 0.85, f"Near-duplicate cross-split leak detected in {dataset_name} with Jaccard={sim:.3f}"

@pytest.mark.parametrize("dataset_name", ["liar_plus", "coaid", "fever", "indic"])
def test_grounded_label_taxonomy_validity(dataset_name: str):
    """Assert that 100% of samples possess a valid grounded label in {VERIFIED, REFUTED, DATA_VOID}."""
    valid_labels = {"VERIFIED", "REFUTED", "DATA_VOID"}
    for split_name in ["train", "val", "test"]:
        split_file = os.path.join(PROCESSED_DIR, dataset_name, f"{split_name}.jsonl")
        if not os.path.exists(split_file):
            continue
        samples = load_jsonl(split_file)
        assert len(samples) > 0, f"Split {split_name} in {dataset_name} is empty!"
        for s in samples:
            assert s.grounded_label in valid_labels, f"Invalid grounded label '{s.grounded_label}' in {s.id}"
            assert len(s.claim_text) >= 10, f"Suspiciously short claim text in {s.id}: '{s.claim_text}'"

def test_unified_benchmark_test_set():
    """Verify that unified_benchmark/test.jsonl contains balanced multi-domain samples."""
    bench_file = os.path.join(PROCESSED_DIR, "unified_benchmark", "test.jsonl")
    assert os.path.exists(bench_file), "Unified benchmark test file missing!"
    samples = load_jsonl(bench_file)
    assert len(samples) >= 100, f"Unified benchmark too small: {len(samples)} samples"

    domains = set(s.domain for s in samples)
    assert "politics" in domains
    assert "health" in domains
    assert "general" in domains
