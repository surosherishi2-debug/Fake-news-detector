# Phase Execution Plan & Quality Gates (PHASES.md)

**Target:** Advance TruthLens-Omni from ~20% prototype to a credible ~50% milestone accepted by an industry expert panel as a complete, reproducible system.

---

## Phase Matrix

| Phase | Title | Scope Summary | Gate Criteria | Status |
|---|---|---|---|---|
| **Phase 0** | **Audit and Setup** | Repo audit, test verification, README claims audit, governance setup, environment lockfile. | Repo audit complete, all existing tests verified, governance files active, user approval received. | **DONE (GATE PASSED)** |
| **Phase 1** | **Literature and Repository Research** | Empirical literature review (LIAR, CoAID, FEVER, FakeNewsNet, HGT, TextAttack, etc.), repository checks, synthesis. | Synthesis approved, adopted ideas list and datasets approved by user. | **DONE (GATE PASSED)** |
| **Phase 2** | **Data Foundation** | Download, checksum, clean, deduplicate, and split approved datasets (leakage testing). Datasheets. | Zero leakage confirmed; datasheets and automated data tests pass. | **DONE (GATE PASSED)** |
| **Phase 3** | **Model Ladder and Evaluation** | Baselines (TF-IDF + LR/SVM), Deep Learning (BiLSTM/CNN), Transformers (English & Multilingual), CEAM evidence model with temporal ablation. Full evaluation protocol (Accuracy, F1, ECE, TextAttack). | Master `docs/RESULTS.md` generated strictly from `experiments/`; error analysis of >=30 samples. | **DONE (GATE READY)** |
| **Phase 4** | **Retrieval, Explainability, Abstention** | Dense retrieval + vector index + re-ranking; SHAP/LIME explanation trail; formal DATA_VOID calibration. | Live demo of 6 curated claim categories (real, fake, satire, data void, adversarial, multilingual). | PENDING |
| **Phase 5** | **Graph / Cascade Module** | Honest scope: Either train on real propagation data or relabel "SIMULATED DEMO" across UI and reports. | Explicit choice logged in `DECISIONS.md` and UI updated. | PENDING |
| **Phase 6** | **Engineering and MLOps** | Architecture refactoring, unit/integration test coverage >=70%, pre-commit/ruff/black, Docker Compose reproduction. | Fresh clone reproduction via `docker compose up` and single benchmark reproduction command. | PENDING |
| **Phase 7** | **Responsible AI and Packaging** | Model card, bias/topic/language analysis, running paper assembly, defense presentation dossier. | Complete reproducible submission package approved. | PENDING |
