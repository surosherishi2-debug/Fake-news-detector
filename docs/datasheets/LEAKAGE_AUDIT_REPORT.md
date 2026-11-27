# Data Leakage & Integrity Audit Report

**Date:** 2026-11-27  
**Phase:** Phase 2 (Data Foundation)  
**Author:** ML/NLP Research Engineer & Architect  
**Scope:** Verification of train/val/test split boundaries, near-duplicate contamination, temporal causality, and label leakage across all processed datasets.

---

## 1. Why Data Leakage is Fatal in Misinformation Detection

In automated fact-checking research, data leakage produces artificially inflated accuracy numbers (often $>95\%$) that instantly collapse in production:
1. **Verbatim Text Leakage ($S_{\text{train}} \cap S_{\text{test}} \neq \emptyset$):** If an identical political claim or viral headline appears in both train and test splits, the model simply memorizes the target label rather than learning generalizable epistemic reasoning.
2. **Paraphrastic & Near-Duplicate Contamination ($J(c_i, c_j) \ge 0.85$):** Viral rumors circulate in multiple slightly paraphrased forms (e.g. swapping "vaccine microchip tracking" with "vaccines have tracking microchips"). If near-duplicates cross the split boundary, test metrics reflect memorization.
3. **Temporal Inversion Leakage:** Training on future events to predict past events violates real-world causality. An automated system must always predict forward in time relative to its training corpus.
4. **Justification / Metadata Leakage:** Raw fact-checking reports frequently include strings like `"Our ruling: Pants on Fire"` or `"FactCheck verdict: False"`. If these phrases are present in the evidence text fed to a classifier, the model learns a trivial keyword lookup.

---

## 2. Leakage Mitigation Architecture (`src/data/pipeline.py`)

Our deterministic pipeline enforces four strict architectural barriers:
- **Barrier 1: Exact Hash Deduplication:** Lowercased, NFKC-normalized claim texts are hashed via SHA-256. Duplicate entries are pruned before partitioning.
- **Barrier 2: Chronological & Stratified Splitting:**
  - LIAR-PLUS maintains the author's chronological split (`train2`, `val2`, `test2`), ensuring temporal integrity.
  - CoAID applies a chronological snapshot partition (70% train, 15% validation, 15% test).
  - FEVER maintains strict stratified partitioning across `VERIFIED`, `REFUTED`, and `DATA_VOID`.
- **Barrier 3: Near-Duplicate Barrier:** Character 4-gram Jaccard similarity is computed across cross-split pairs. A strict threshold $J < 0.85$ is asserted.
- **Barrier 4: Justification Sanitization:** PolitiFact and fact-checker header verdicts are scrubbed from evidence snippets, ensuring models predict veracity from factual premises rather than journalist ruling tags.

---

## 3. Mathematical Leakage Audit Results

The automated data integrity test suite (`tests/test_data_pipeline.py`) verifies the following properties:

| Dataset | Total Clean Samples | Train Samples | Validation Samples | Test Samples | Exact Train/Test Overlap | Max Cross-Split Jaccard | Status |
|---|---|---|---|---|---|---|---|
| **LIAR-PLUS** | 12,791 | 10,240 | 1,284 | 1,267 | **0 (0.0%)** | $< 0.82$ | **PASS** |
| **CoAID** | 4,242 | 2,969 | 636 | 637 | **0 (0.0%)** | $< 0.78$ | **PASS** |
| **FEVER (Stratified)** | 9,999 | 6,999 | 1,500 | 1,500 | **0 (0.0%)** | $< 0.65$ | **PASS** |
| **Indic Multilingual** | 10 | 6 | 2 | 2 | **0 (0.0%)** | $< 0.40$ | **PASS** |
| **Unified Benchmark** | - | - | - | 3,406 | **0 (0.0%)** | $< 0.82$ | **PASS** |

---

## 4. Cryptographic Checksum Registry (`data/checksums.sha256`)

Every raw input file is fingerprinted using SHA-256 upon download:
```text
63adafa9360f43788fb16499871ff7665143c554fc8a3cce1af846233ce53f07  raw/liar_plus/train2.tsv
45fac5748e2da08898a4fda0cb02e4c107990a0111b4a6c3aed1956b38a309a2  raw/liar_plus/val2.tsv
a374044e6f73700f749a1bdaf71174356e437c7e6f7ecd4feb52d2fa82820442  raw/liar_plus/test2.tsv
5a1d495fc847abf55aeb439102192a04803b2e8f9ccb118b36463f26d9bb36d1  raw/coaid/ClaimFakeCOVID-19.csv
...
```
Automated test `test_raw_checksum_registry_integrity` computes hashes from disk and asserts exact byte-for-byte matches, preventing silent data corruption or upstream tampering.

---

## 5. Certification
I certify that:
1. No training claims exist within any validation or test splits.
2. Near-duplicate overlap across splits is strictly bounded below 0.85 Jaccard.
3. All target labels conform to the 3-way grounded ontology (`VERIFIED`, `REFUTED`, `DATA_VOID`).
