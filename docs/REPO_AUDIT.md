# Repository Audit: TruthLens-Omni

**Date:** 2026-11-27  
**Commit/Branch:** `phase-0-audit-setup`  
**Auditor:** ML/NLP Research Engineer & Architect  
**Objective:** Comprehensive code, architecture, and empirical reality audit of base repository `https://github.com/surosherishi2-debug/Fake-news-detector`.

---

## 1. Executive Summary

The base repository presents an ambitious epistemic intelligence and publishing integrity dashboard combining claim decomposition, fact-check retrieval, temporal decay weighting, social cascade analysis, and matrix factorization.

However, an exhaustive line-by-line inspection reveals that **the machine learning / deep learning core is primarily conceptual or simulated**:
- The headline benchmark figures (e.g. 94.8% TruthLens accuracy, 86.5% BERT-Base) are **100% hard-coded dictionaries** in `src/models/evaluator.py`. No training, evaluation loops, or real inference runs produce these numbers.
- The PyTorch neural models (`CEAMTruthLensModel` in `src/models/ceam_model.py` and `HeteroGraphEncoder` in `src/graph/hgt_encoder.py`) contain valid forward definitions but **possess zero trained weights**, have no training scripts, and are **completely disconnected** from the production verification pipeline (`src/fusion/truthlens_engine.py`).
- The benchmark datasets (`PuneFakeNews-2024`, `LIAR-Plus`, `CoAID`) in `src/data/dataset_loader.py` are **synthetic Python-inlined mock lists** containing 4 to 8 handwritten samples each. No genuine academic datasets are ingested or downloaded.
- The core runtime verification logic in `TruthLensEngine` operates as a **heuristic rule-based decision tree** with regex pattern matching, keyword searching against a 3-item hard-coded fact registry, and fixed linear weight combinations.

---

## 2. Component Inventory & Reality Audit

| Component / File | What it claims to be | Current Reality | Real, Simulated, or Hard-coded? | Trained Weights? |
|---|---|---|---|---|
| `src/models/ceam_model.py` | Context-Enhanced Attention Mechanism (CEAM) deep neural architecture | Syntactically valid PyTorch `nn.Module` defining Cross-Attention and Gated Fusion. | Real architecture, but **completely disconnected** from production verification engine. | **NO**. Instantiated with random initialization. No weight checkpoints exist. |
| `src/models/evaluator.py` | Empirical benchmark evaluation suite across models and datasets | Returns fixed static Pydantic objects containing hard-coded numbers (e.g. 68.4%, 74.2%, 86.5%, 94.8%). | **HARD-CODED**. No evaluation is executed. | **NO**. |
| `src/models/adversarial_tester.py` | Adversarial stress tester (TextFooler & DeepWordBug) | Regex-based word replacer using a fixed dictionary of 12 keyword synonym lists and random character swaps/drops. | **SIMULATED / HEURISTIC**. Does not use TextAttack or gradient-based word importance. | **NO**. |
| `src/graph/hgt_encoder.py` | Heterogeneous Graph Transformer (HGT) cascade encoder | Contains a 3-layer PyTorch encoder (`HeteroGraphEncoder`) and a heuristic analyzer (`CascadeTopologyAnalyzer`). | Encoder is real PyTorch, but **unused in verification**. Analyzer is a rule-based formula based on node attributes. | **NO**. |
| `src/graph/consensus_matrix.py` | Bipartisan Matrix Factorization for Community Notes | Fully functional SGD-based matrix factorization optimizing $r_{ui} \approx \mu + b_u + b_i + p_u^\top q_i$ on rating triples. | **REAL**. Functional classical ML implementation using NumPy. | Real optimization executed at runtime (on-the-fly fit). |
| `src/nlp/temporal_decay.py` | Exponential temporal credibility decay $w(t) = \exp(-\lambda \Delta t)$ | Exact mathematical exponential decay calculation with domain-specific $\lambda$ mapping. | **REAL**. Fully functional mathematical utility. | Fixed hyperparameters ($\lambda \in [0.01, 0.40]$). |
| `src/nlp/claim_decomposer.py` | Claim extraction & check-worthiness scoring | Sentence boundary splitting via regex, keyword pattern matching, and entity heuristic extraction. | **REAL HEURISTIC**. Does not use trained ClaimBuster RoBERTa model. | **NO**. Hand-crafted regex weights. |
| `src/nlp/synthetic_detector.py` | Forensic detector for AI-generated text | Calculates sentence length standard deviation (burstiness), Type-Token Ratio (TTR), Top-10 word lookup, and regex catchphrases. | **REAL HEURISTIC**. Based on statistical heuristics rather than trained perplexity / watermarking models. | **NO**. |
| `src/nlp/preflight_auditor.py` | Draft article integrity auditor | Orchestrates `ClaimDecomposer` and `FactCheckClient` with clickbait regex scoring. | **REAL HEURISTIC**. | **NO**. |
| `src/retrieval/fact_check_client.py` | Google Fact Check API & ClaimReview client | Real HTTP client for Google Fact Check Tools API with fallback to `OFFLINE_FACT_REGISTRY`. | **REAL API CLIENT + HARD-CODED FALLBACK** (3 hard-coded entries). | N/A (Retrieval). |
| `src/retrieval/url_scraper.py` | Live DOM content extractor | BeautifulSoup scraper extracting title, meta tags, and body paragraphs. | **REAL**. Functional HTML scraper with timeout handling. | N/A. |
| `src/data/dataset_loader.py` | Academic benchmark dataset loader | In-memory Python lists: 8 samples for PuneFakeNews, 4 for LIAR-Plus, 2 for CoAID. | **HARD-CODED MOCK**. No real datasets loaded or downloaded. | N/A. |
| `src/data/news_database.py` | SQLite epistemic store (`epistemic_store.sqlite3`) | Real SQLite persistence schema storing articles, claims, entities, and edges. Seeds 12 sample articles. | **REAL PERSISTENCE** with hard-coded seed data. | N/A. |
| `src/data/rss_crawler.py` | Real-time RSS feed crawler | Ingests XML feeds from PIB/BBC with fallback to 3 hard-coded cached articles. | **REAL PARSER + HARD-CODED FALLBACK**. | N/A. |
| `src/fusion/truthlens_engine.py` | Master Tri-Modal Orchestrator | Linear weighted sum of semantic refutation, graph risk, and publisher reputation with veto rules. | **REAL RULE ENGINE**. Does not execute `CEAMTruthLensModel`. | **NO**. |
| `src/api/server.py` | FastAPI REST microservice | Complete FastAPI application exposing 15+ endpoints, serving SPA and JSON APIs. | **REAL**. Fully functional async web server. | N/A. |
| `src/core/auth.py` | Epistemic identity & JWT auth | PBKDF2 password hashing, HS256 JWT tokens, SQLite user store, and simulated SSO. | **REAL AUTH SERVICE** (SSO is simulated mock). | N/A. |
| `chrome-extension/` | Manifest v3 Chrome extension | Background service worker, context menu, popup interface calling `localhost:8000/api/v1/verify`. | **REAL BROWSER EXTENSION**. | N/A. |

---

## 3. Disconnected & Inactive Modules

1. **`CEAMTruthLensModel` (`src/models/ceam_model.py`):**
   - Implements CrossAttention and Gated Fusion in PyTorch.
   - **Status:** Orphaned. It is only imported in `tests/test_ceam_and_benchmarks.py` to assert that synthetic random tensors pass through forward without throwing a shape error. It is **never called** by `TruthLensEngine` or `src/api/server.py`.
2. **`HeteroGraphEncoder` (`src/graph/hgt_encoder.py`):**
   - Implements linear projection layers for heterogeneous node types.
   - **Status:** Orphaned. It is tested in `tests/test_hgt_cascade.py` with random tensors, but `CascadeTopologyAnalyzer` and `TruthLensEngine` never instantiate or call it.
3. **`ModelEvaluator` (`src/models/evaluator.py`):**
   - **Status:** Fabricated output. `run_benchmark_suite()` does not execute any model inference, does not compute metrics, and does not test any weights. It returns static pre-populated metrics rows.

---

## 4. Test Suite Audit

- **Test Discovery:** 10 test files in `tests/`.
- **Test Count:** 38 collected test items (all 38 PASSED in 9.60s on Python 3.12).
- **README Discrepancy:** The README badge states:
  `[![Tests Status](https://img.shields.io/badge/Tests-26%2F26%20Passing%20(100%25)-brightgreen)]`
  In reality, the repository contains 38 tests, indicating the README was not updated after tests were added.
- **Coverage Quality:** The tests thoroughly verify Pydantic schemas, edge cases (empty strings, missing dates, malformed URLs), matrix factorization convergence, and API HTTP routes. However, **none of the tests measure actual machine learning model performance or generalization on real data**.

---

## 5. Summary of Gaps to Bridge (Phase 1 through Phase 6)

1. **Real Data Foundation:** Replace hard-coded 8-sample dataset mocks with verified, checksummed benchmark datasets (LIAR, CoAID, FEVER, ISOT, etc.).
2. **True Model Training & Weights:** Build deterministic, reproducible pipelines to train baselines (TF-IDF + Ridge/SVM), deep learning models, Transformers, and multimodal evidence cross-attention.
3. **True Evaluation Protocol:** Measure genuine macro-F1, ECE calibration, cross-dataset transfer, and true adversarial robustness using real libraries (TextAttack).
4. **Integration:** Connect the trained models directly into the `TruthLensEngine` and FastAPI runtime.
