# TruthLens-Omni: Project Ledger

**Source of Truth:** External memory for all completed tasks across project phases.  
**Rule Reference:** Non-Negotiable Operating Rule R4 ("External memory is the source of truth, not your context. After every completed task, append an entry to docs/PROJECT_LEDGER.md.").

---

## [2026-11-27 17:35] Phase 0.Task 0.1 - Comprehensive Repository Audit
- **Goal:** Read the entire base repository (`src/`, `tests/`, `chrome-extension/`, `run.py`, `requirements.txt`, `render.yaml`, `README.md`) and produce an exhaustive audit detailing what exists, what is real, what is simulated, what is hard-coded, and what has no trained weights.
- **What I did (files created/changed):**
  - Read all source files in `src/`, `tests/`, `chrome-extension/`, `run.py`, `requirements.txt`, `render.yaml`, and `README.md`.
  - Created `docs/REPO_AUDIT.md` documenting module inventory, orphaned architectures (`CEAMTruthLensModel`, `HeteroGraphEncoder`), and hardcoded benchmarks in `src/models/evaluator.py`.
- **Commands run + result:**
  - `Get-ChildItem -Recurse -File` -> 49 files discovered.
  - Inspected line counts and code logic across all subdirectories.
- **Evidence it works:** `docs/REPO_AUDIT.md` written and cross-referenced with exact line numbers.
- **Sources used:** Base repository `https://github.com/surosherishi2-debug/Fake-news-detector`.
- **Decisions made:** D01 (Document base code as primarily heuristic rule-based with disconnected PyTorch scaffolding).
- **Open questions raised:** Q01, Q02.
- **Status:** DONE.
- **Next task:** Phase 0.Task 0.2.

---

## [2026-11-27 17:36] Phase 0.Task 0.2 - Baseline Test Suite & Runtime App Execution
- **Goal:** Run existing automated tests and the application runner to record exact terminal outputs and verify baseline functionality.
- **What I did (files created/changed):**
  - Executed pytest over the full test suite (`tests/`).
  - Executed `python run.py --demo` to record terminal demo output.
  - Tested FastAPI server health endpoint `/api/v1/health` via TestClient.
- **Commands run + result:**
  - `python -m pytest tests -v` -> 38 passed in 9.60s (Python 3.12.10, pytest 9.1.1).
  - `python run.py --demo` -> Successfully verified 3 sample claims (viral microchip, Onion satire, zero-assumption data-void).
  - `python -c "from src.api.server import app; from fastapi.testclient import TestClient; ..."` -> Status 200 `{'status': 'healthy', 'service': 'TruthLens-Omni', 'version': '1.0.0', 'lambda_decay': 0.1, 'fact_check_api_configured': False}`.
- **Evidence it works:** Terminal test log recorded 38/38 passing tests with zero test failures.
- **Sources used:** N/A.
- **Decisions made:** D02 (Confirm existing test baseline passes completely; reconcile README badge discrepancy).
- **Open questions raised:** None.
- **Status:** DONE.
- **Next task:** Phase 0.Task 0.3.

---

## [2026-11-27 17:38] Phase 0.Task 0.3 - Existing README Claims Audit
- **Goal:** Audit every claim in the base README against evidence in the codebase.
- **What I did (files created/changed):**
  - Created `docs/CLAIMS_AUDIT.md` auditing 14 specific claims from `README.md`.
  - Classified each claim as VERIFIED, REFUTED, or UNVERIFIED with exact line-level evidence.
- **Commands run + result:** Static code analysis comparing README text against `src/models/evaluator.py`, `src/data/dataset_loader.py`, `src/graph/hgt_encoder.py`, and `src/models/ceam_model.py`.
- **Evidence it works:** `docs/CLAIMS_AUDIT.md` complete with master claims register.
- **Sources used:** Base `README.md`.
- **Decisions made:** D03 (Treat all README metrics as unverified hypotheses and bar them from future reports until reproduced).
- **Open questions raised:** Q03.
- **Status:** DONE.
- **Next task:** Phase 0.Task 0.4.

---

## [2026-11-27 17:42] Phase 0.Task 0.4 - Foundational Governance Setup & Environment Pinning
- **Goal:** Create all Section 2 governance files, initialize the running paper in `docs/paper/`, establish `experiments/`, pin dependencies to a lockfile, and prepare Phase 0 Gate.
- **What I did (files created/changed):**
  - Created `docs/DECISIONS.md`, `docs/OPEN_QUESTIONS.md`, `docs/SOURCES.md`, `docs/FAILURES.md`, `docs/BACKLOG.md`, `docs/PHASES.md`, `docs/RESULTS.md`.
  - Created running paper scaffolding: `docs/paper/01_introduction.md`, `02_related_work.md`, `03_method.md`, `04_experiments.md`, `05_results.md`, `06_discussion.md`, `07_limitations.md`, `references.bib`.
  - Created `experiments/` directory with `.gitkeep`.
  - Generated `requirements-lock.txt` pinning exact versions of all installed packages.
- **Commands run + result:**
  - `pip freeze > requirements-lock.txt`
  - Created directories and files.
- **Evidence it works:** All Section 2 files verified to exist on disk.
- **Sources used:** Base workspace.
- **Decisions made:** D04 (Pin Python 3.12 environment with `requirements-lock.txt`).
- **Open questions raised:** None.
- **Status:** DONE.
- **Next task:** Phase 0 Gate Review & User Approval.

---

## [2026-11-27 17:51] Phase 1.Task 1.1–1.3 - Literature & Repository Research and Synthesis
- **Goal:** Investigate state-of-the-art literature in misinformation detection, claim verification, and fact-checking (including recent 2024–2026 works); verify repository activities, licenses, and data access methods; author `docs/paper/02_related_work.md` and `docs/RESEARCH_SYNTHESIS.md`; and define the adopted-ideas and dataset lists for user gate approval.
- **What I did (files created/changed):**
  - Created `phase-1-research` branch.
  - Performed systematic web searches on seed topics (LIAR-Plus, CoAID, FEVER, FakeNewsNet, ISOT, Community Notes, ClaimBuster, CheckThat! Lab, TextAttack, MuRIL, XLM-R).
  - Verified live data accessibility via Python HTTP tests:
    - LIAR-PLUS raw TSV fetch (`train2.tsv` from `Tariq60/LIAR-PLUS`).
    - CoAID raw CSV fetch (`ClaimFakeCOVID-19.csv` from `cuilimeng/CoAID`).
    - FEVER raw JSONL fetch (`train.jsonl` from `fever.ai`).
  - Cataloged 14 active sources and verified citations in `docs/SOURCES.md`.
  - Authored comprehensive `docs/RESEARCH_SYNTHESIS.md` articulating the 4 critical industry failure modes and proposing 5 core adopted ideas and 4 candidate datasets.
  - Authored `docs/paper/02_related_work.md` covering 6 subdisciplines with BibTeX entries in `docs/paper/references.bib`.
  - Logged architectural decisions `D06` and `D07` in `docs/DECISIONS.md`.
- **Commands run + result:**
  - Python tests fetching raw sample lines from GitHub `Tariq60/LIAR-PLUS`, `cuilimeng/CoAID`, and `fever.ai` -> All succeeded with valid line parses.
  - Verified package availability (`sentence-transformers 6.2.0`, `scikit-learn 1.9.0`, `torch 2.13.0`, `transformers 5.20.2`).
- **Evidence it works:** Verified file presence on disk: `docs/RESEARCH_SYNTHESIS.md`, `docs/paper/02_related_work.md`, `docs/paper/references.bib`, `docs/SOURCES.md`, `docs/DECISIONS.md`.
- **Sources used:** `S06` (LIAR-PLUS), `S07` (CoAID), `S08` (FEVER), `S09` (FakeNewsNet), `S10` (Community Notes), `S11` (TextAttack), `S12` (MuRIL), `S13` (Sentence-Transformers), `S14` (Scikit-Learn).
- **Decisions made:** `D06` (5 Core Adopted Ideas), `D07` (4 Candidate Benchmark Datasets).
- **Open questions raised:** None (Q01 addressed: synthetic `PuneFakeNews-2024` replaced with genuine Indic and open benchmarks).
- **Status:** DONE.
- **Next task:** Phase 1 Gate Review: User approval of the Adopted Ideas List and Dataset List.

---

## [2026-11-27 18:00] Phase 2.Task 2.1–2.3 - Data Foundation & Train/Test Leakage Elimination
- **Goal:** Download, version, and verify SHA-256 checksums for the 4 approved datasets; implement a deterministic cleaning, deduplication, and splitting pipeline (`src/data/pipeline.py`); author comprehensive datasheets in `docs/datasheets/`; and prove zero train/test leakage with automated pytest tests.
- **What I did (files created/changed):**
  - Created `phase-2-data-foundation` branch.
  - Created `src/data/downloader.py` and downloaded raw files for LIAR-Plus (8.7 MB), CoAID (1.8 MB), FEVER (2.7 MB), and Indic Multilingual (7 KB).
  - Generated master `data/checksums.sha256` recording cryptographic hashes for all 9 raw source files.
  - Created `src/data/pipeline.py`:
    - NFKC Unicode normalization, whitespace collapsing.
    - Exact hash deduplication and near-duplicate detection ($J \ge 0.85$).
    - Cross-split anti-leakage barrier: purged 9 verbatim duplicate training claims that contaminated the evaluation set in original LIAR-Plus.
    - Standardized tripartite label mapping (`VERIFIED`, `REFUTED`, `DATA_VOID`).
    - Partitioned each dataset into `train.jsonl`, `val.jsonl`, `test.jsonl` in `data/processed/`.
    - Compiled unified cross-domain test suite of 2,931 samples in `data/processed/unified_benchmark/test.jsonl`.
  - Created `tests/test_data_pipeline.py` with 14 automated integrity and leakage tests.
  - Authored datasheets: `LIAR_PLUS_DATASHEET.md`, `COAID_DATASHEET.md`, `FEVER_DATASHEET.md`, `INDIC_MULTILINGUAL_DATASHEET.md`, and `LEAKAGE_AUDIT_REPORT.md` in `docs/datasheets/`.
  - Logged decision `D08` in `docs/DECISIONS.md`.
  - Updated `docs/paper/04_experiments.md` with exact dataset statistics.
- **Commands run + result:**
  - `python src/data/downloader.py` -> Successfully fetched all 9 raw source files and wrote `data/checksums.sha256`.
  - `python src/data/pipeline.py` -> Cleaned and saved:
    - LIAR-PLUS: 10,212 train, 1,284 val, 1,267 test.
    - CoAID: 1,611 train, 345 val, 346 test.
    - FEVER: 6,137 train, 1,315 val, 1,316 test.
    - Indic: 6 train, 2 val, 2 test.
    - Unified Benchmark: 2,931 test samples.
  - `python -m pytest tests/test_data_pipeline.py -v` -> **14/14 tests passed in 0.73s** (0 exact overlap, Jaccard < 0.85, checksums matched).
  - `python -m pytest tests -v` -> **52/52 tests passed in 6.71s** (full regression suite clean).
- **Evidence it works:** Real terminal output showing 52 passed tests; `data/checksums.sha256` matching; `data/processed/` JSONL files present on disk.
- **Sources used:** `S06`, `S07`, `S08`, `S12` in `docs/SOURCES.md`.
- **Decisions made:** `D08` (Strict Cross-Split Anti-Leakage Deduplication).
- **Open questions raised:** None.
- **Status:** DONE.
- **Next task:** Phase 3.Task 3.1–3.7 — Model Ladder & Evaluation Protocol.

---

## [2026-11-27 18:38] Phase 3.Task 3.1–3.7 - Model Ladder & Comprehensive Evaluation Protocol
- **Goal:** Implement, train, evaluate, and calibrate an empirical model ladder spanning Classical ML (TF-IDF + LR/SVM/NB), Deep Learning (BiLSTM), Pre-trained Transformers (English all-MiniLM-L6-v2 & Multilingual paraphrase-multilingual-MiniLM-L12-v2), and Evidence-Aware CEAM (Gated Cross-Attention with temporal decay ablation). Execute multi-seed stability, Expected Calibration Error (ECE), adversarial stress-testing (TextFooler), qualitative error analysis (35 failure cases), and programmatically generate `docs/RESULTS.md` directly from `experiments/*/metrics.json`.
- **What I did (files created/changed):**
  - Created `phase-3-model-ladder` branch.
  - Resolved `Q04` in `docs/OPEN_QUESTIONS.md` (CPU-optimized training protocol).
  - Created `src/evaluation/metrics.py` implementing mathematically rigorous Accuracy, Macro-F1, per-class F1, multi-class One-vs-Rest ROC-AUC, 10-bin Expected Calibration Error (ECE), and Brier Score.
  - Created `tests/test_evaluation_metrics.py` (4 automated tests).
  - Created `src/models/baselines.py`: trained TF-IDF (1-2 ngrams, 10k features) with Logistic Regression, Calibrated Linear SVM, and Multinomial Naive Bayes across seeds 42, 43, 44. Logged to `experiments/exp01_tfidf_baselines/`.
  - Created `src/models/deep_models.py`: built `TokenVocab`, PyTorch 2-layer `BiLSTMClassifier`, mini-batch DataLoader with early stopping. Trained on CPU and logged checkpoints and metrics to `experiments/exp02_bilstm/`.
  - Created `src/models/transformer_models.py`: trained neural classification heads over dense semantic representations from `sentence-transformers/all-MiniLM-L6-v2` and `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Logged to `experiments/exp03_transformer_english/` and `experiments/exp04_transformer_multilingual/`.
  - Enhanced `src/models/ceam_model.py` and created `src/models/ceam_trainer.py`: trained CEAM with paired (claim, evidence) cross-attention, domain-adaptive temporal decay $w(t) = \exp(-\lambda \Delta t)$, and executed formal ablation ($w(t)=\exp(-\lambda \Delta t)$ vs $w(t)=1.0$) logged in `experiments/exp05_ceam_temporal/` and `experiments/exp06_ceam_notemporal/`.
  - Created `src/evaluation/adversarial_evaluation.py`: evaluated models on clean vs 20% synonym-perturbed test claims; logged results to `experiments/adversarial_metrics.json`.
  - Created `src/evaluation/error_analysis.py`: extracted and classified 35 concrete empirical failures across 6 structural categories into `docs/ERROR_ANALYSIS.md`.
  - Created `src/evaluation/generate_results_table.py`: programmatically rendered all results tables in `docs/RESULTS.md` strictly from code.
  - Updated running paper `docs/paper/05_results.md` with verified empirical findings.
  - Created `tests/test_model_ladder.py` (6 unit/regression tests).
  - Logged architectural decisions `D09` and `D10` in `docs/DECISIONS.md`.
- **Commands run + result:**
  - `python -m src.models.baselines` -> Logged `exp01_tfidf_baselines` (LR Acc: 58.34%, F1: 51.83%, ECE: 0.0287; SVM Acc: 56.06%, F1: 47.40%; NB Acc: 53.97%, F1: 51.03%).
  - `python -m src.models.deep_models` -> Logged `exp02_bilstm` (Acc: 57.83%, F1: 54.10%, ECE: 0.0530, checkpoint saved).
  - `python -m src.models.transformer_models` -> Logged `exp03_transformer_english` (Acc: 59.84%, F1: 55.17%, ECE: 0.0736, ROC-AUC: 0.7802) and `exp04_transformer_multilingual` (Acc: 58.79%, F1: 54.05%, Indic Acc: 100%).
  - `python -m src.models.ceam_trainer` -> Logged `exp05_ceam_temporal` (Acc: 54.55%, F1: 36.16%, ECE: 0.0413) and `exp06_ceam_notemporal` (Acc: 58.27%, F1: 40.39%, ECE: 0.0405; Delta F1: -4.23%).
  - `python -m src.evaluation.adversarial_evaluation` -> Logged `experiments/adversarial_metrics.json` (Transformer retention: 96.17%, LR retention: 93.85%).
  - `python -m src.evaluation.error_analysis` -> Extracted 35 failure cases into `docs/ERROR_ANALYSIS.md`.
  - `python -m src.evaluation.generate_results_table` -> Generated `docs/RESULTS.md`.
  - `python -m pytest tests -v` -> **62/62 tests passed in 22.22s** (full regression suite clean).
- **Evidence it works:** All 6 experiment directories exist in `experiments/` with `config.json`, `metrics.json`, and checkpoints; `docs/RESULTS.md` compiled; `pytest tests -v` passed 62/62.
- **Sources used:** `S06`, `S07`, `S08`, `S11`, `S12`, `S13`, `S14` in `docs/SOURCES.md`.
- **Decisions made:** `D09` (Multi-Tier Model Ladder & Weight Checkpoints), `D10` (Tripartite Taxonomy & Temporal Ablation).
- **Open questions raised:** None (`Q04` resolved).
- **Status:** DONE.
- **Next task:** Phase 3 Gate Review & User Approval to proceed to Phase 4 (Retrieval, Explainability, Abstention).



