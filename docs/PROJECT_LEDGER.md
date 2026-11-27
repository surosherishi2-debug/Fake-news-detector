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
