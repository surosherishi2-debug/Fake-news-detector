# Design Decisions Log (DECISIONS.md)

**Rule Reference:** Non-Negotiable Operating Rule R4 ("Record each design decision: context, options, choice, why").

---

### [D01] Baseline Architectural Reality: Treat Base Code as Heuristic Prototype
- **Context:** Base repo presents itself as a fully trained tri-modal neuro-symbolic platform with published benchmark scores (94.8% accuracy). Line-by-line inspection proved the benchmark evaluator outputs static hardcoded constants and PyTorch models have zero trained weights.
- **Options Considered:**
  1. Pretend the existing model code is functional and attempt to wrap it.
  2. Acknowledge base code as an interactive UI and heuristic rule prototype; build the real ML/DL model ladder on clean, reproducible foundations.
- **Choice:** Option 2.
- **Rationale:** Adheres strictly to R1 (No assumptions) and R2 (No fabricated numbers). A credible industry-grade system requires real trained weights and reproducible metrics.

---

### [D02] Reconcile Test Baseline: 38 Passing Tests
- **Context:** `README.md` badge states 26/26 tests passing, whereas test discovery executed 38 tests across 10 test files.
- **Options Considered:**
  1. Keep README claim untouched.
  2. Document the discrepancy in `docs/CLAIMS_AUDIT.md` and adopt the 38 passing tests as the real regression baseline.
- **Choice:** Option 2.
- **Rationale:** 38 tests currently pass. We maintain all 38 existing tests as a regression suite so no refactoring breaks existing UI or API contracts.

---

### [D03] Purge Fabricated Numbers from Results and Reports
- **Context:** Existing README and `src/models/evaluator.py` cite specific numbers (94.2% accuracy under TextFooler, 28% BERT drop, etc.).
- **Options Considered:**
  1. Continue citing these figures as "initial results".
  2. Flag all such numbers as UNVERIFIED / REFUTED in `docs/CLAIMS_AUDIT.md` and bar them from `docs/RESULTS.md` until genuinely trained and evaluated in `experiments/`.
- **Choice:** Option 2.
- **Rationale:** R2 strictly dictates that every metric must come from a log/run file in `experiments/` that we produce.

---

### [D04] Pin Python 3.12 Environment with `requirements-lock.txt`
- **Context:** R9 requires fixing random seeds and pinning dependency versions with a lockfile for deterministic reproduction.
- **Options Considered:**
  1. Use unpinned `requirements.txt` with loose `>=` bounds.
  2. Generate a comprehensive `requirements-lock.txt` using `pip freeze` from the verified working Python 3.12 environment.
- **Choice:** Option 2.
- **Rationale:** Guarantees that any judge, researcher, or CI runner can reproduce the exact environment.

---

### [D05] Explicit Labeling of Simulated / Heuristic Components
- **Context:** R3 requires: "Any simulated or synthetic component must be labelled 'SIMULATED' in code, UI, docs and reports."
- **Options Considered:**
  1. Leave simulated components unmarked.
  2. Formally label heuristic adversarial perturbation, synthetic dataset mocks, and social cascade heuristics as "SIMULATED / HEURISTIC" across documentation, UI, and code.
- **Choice:** Option 2.
- **Rationale:** Complete transparency for industry panel evaluation.

---

### [D06] Selection of the 5 Core Adopted Ideas for the ~50% Milestone
- **Context:** Phase 1 requires identifying 3–5 specific state-of-the-art ideas with justifications and citations to bridge from the base prototype to a credible system.
- **Options Considered:**
  1. Rely exclusively on text-only fine-tuning (e.g. RoBERTa text classifier).
  2. Adopt the 5-pillar architecture: (1) Evidence-Conditioned Veracity Modeling with Calibrated Abstention (FEVER/LIAR-Plus); (2) Domain-Adaptive Temporal Decay $w(t)$ (TSVer/Quantemp); (3) Two-Stage Dense Semantic Retrieval (Sentence-BERT + Re-ranking); (4) Adversarial Stress-Testing (TextAttack/TextFooler); and (5) Multilingual Indic Transfer (MuRIL/XLM-R).
- **Choice:** Option 2.
- **Rationale:** Directly addresses the 4 critical failure modes identified in literature (adversarial collapse, temporal obsolescence, closed-world hallucination, and lack of Indic coverage) while preserving the core strengths of the base system.

---

### [D07] Selection of the 4 Benchmark Datasets for Phase 2 Data Foundation
- **Context:** The base repo used 8 synthetic mock dictionaries for `PuneFakeNews-2024`. Real datasets with verified access and open licenses are required.
- **Options Considered:**
  1. Keep synthetic mock data.
  2. Select 4 verified, downloadable open datasets: LIAR-Plus (Political), CoAID (Biomedical/Health), FEVER subset (Grounded entailment & abstention), and Indic Multilingual Benchmark (Hindi/Marathi IFCN debunks).
- **Choice:** Option 2.
- **Rationale:** All 4 datasets were verified this session via direct HTTP fetches, possess open licenses, and cover multiple distinct domains and languages.

---

### [D08] Strict Cross-Split Anti-Leakage Deduplication
- **Context:** Running `tests/test_data_pipeline.py` exposed 9 claims in the original PolitiFact LIAR-PLUS `train2.tsv` that verbatim duplicated claims in `test2.tsv` and `val2.tsv` (e.g. repetitive short policy statements).
- **Options Considered:**
  1. Ignore the 9 leaked claims because they exist in the author's official release.
  2. Protect the validation and test sets by actively purging any training claim that appears in the evaluation splits.
- **Choice:** Option 2.
- **Rationale:** Complete adherence to R1 and R5. Zero tolerance for train/test contamination. The evaluation sets remain pristine, and training claims with identical lowercased text are purged.


