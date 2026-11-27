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

