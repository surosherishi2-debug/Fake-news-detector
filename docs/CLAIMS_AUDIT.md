# Claims Audit: Existing README & Codebase Claims

**Date:** 2026-11-27  
**Rule Reference:** Non-Negotiable Operating Rule R2 ("NO FABRICATED NUMBERS. Every metric... Treat existing README claims as hypotheses. Maintain docs/CLAIMS_AUDIT.md listing each claim as VERIFIED / REFUTED / UNVERIFIED with evidence.")

---

## master Claims Register

| # | Claim in README / Repo | Claim Location | Status | Evidence / Diagnosis |
|---|---|---|---|---|
| C01 | "Tests: 26/26 Passing (100%)" | README.md L7 | **REFUTED** | `pytest tests -v` discovered and executed **38 tests** (100% passed in 9.60s). The badge figure of 26 is stale. |
| C02 | "TruthLens retains 94.2% accuracy under TextFooler synonym substitution" | README.md L228 | **REFUTED (FABRICATED)** | In `src/models/evaluator.py` L114-122, `accuracy=94.8`, `adversarial_f1=87.6`, `robustness_retention=92.4%` are hard-coded static numbers inside `ModelEvaluator.run_benchmark_suite()`. No evaluation was run; no real TextFooler attack was executed. |
| C03 | "Raw BERT models drop by 28% under TextFooler" | README.md L228 | **UNVERIFIED (FABRICATED)** | In `src/models/evaluator.py` L88-97, BERT-Base metrics (`accuracy=86.5`, `adversarial_f1=43.1`, `robustness_retention=49.8%`) are hard-coded static numbers. No BERT model exists in the repo or was benchmarked. |
| C04 | "Tested natively on English, Hindi, and Marathi datasets (`PuneFakeNews-2024`)" | README.md L91, L229 | **REFUTED (SYNTHETIC)** | `PuneFakeNews-2024` in `src/data/dataset_loader.py` L95-216 consists solely of **8 handwritten synthetic dictionaries** embedded directly in Python code. It is not an empirical external dataset. |
| C05 | "Affiliation: MIT-WPU & IIT Bombay AI Lab Framework" | README.md L242 | **UNVERIFIED** | No formal institutional agreement, lab credentials, repository author validation, or institutional email exists in the codebase. Treat as hypothesis. |
| C06 | "Grounding & Standards: IEEE TNN 2024 / EDI.researchpaper.pdf" | README.md L243, `ceam_model.py` L3 | **UNVERIFIED** | No paper file `EDI.researchpaper.pdf` exists in the repository. No IEEE paper citation or DOI is verifiable in the workspace. |
| C07 | "Heterogeneous Graph Transformers (HGT) social cascade embeddings" | README.md L79, L118-120 | **REFUTED (SIMULATED)** | `HeteroGraphEncoder` in `src/graph/hgt_encoder.py` is a simple 3-layer linear neural network (`nn.Linear`), not an HGT (no heterogeneous multi-head graph attention / message passing from PyG). Furthermore, it is **never called** by the verification engine (`truthlens_engine.py`). |
| C08 | "Context-Enhanced Attention Mechanism (CEAM) Cross-Attention" | README.md L113-116 | **PARTIALLY VERIFIED (ARCH ONLY) / UNCONNECTED** | `CrossAttentionLayer` and `CEAMTruthLensModel` in `src/models/ceam_model.py` implement standard scaled dot-product cross-attention in PyTorch. However, it has **zero trained weights** and is **never called** in the end-to-end verification pipeline. |
| C09 | "Community Notes Matrix Factorization (SVD)" | README.md L83-86, L108-111 | **VERIFIED** | `BridgingConsensusEngine` in `src/graph/consensus_matrix.py` implements regularized Stochastic Gradient Descent matrix factorization on rating triples $(u, i, r)$. It mathematically optimizes global intercept, user bias, note helpfulness $b_i$, and latent factors. Tested and functioning in `tests/test_consensus_matrix.py`. |
| C10 | "Temporal Evidence Decay $w(t) = \exp(-\lambda \cdot \Delta t)$" | README.md L103-107 | **VERIFIED** | Implemented mathematically in `src/nlp/temporal_decay.py`. Correctly computes exponential decay with domain-adaptive half-lives. Verified in `tests/test_temporal_decay.py`. |
| C11 | "GLTR Predictability Heatmap & Token Entropy" | README.md L65-69 | **VERIFIED (HEURISTIC)** | `src/nlp/synthetic_detector.py` computes sentence length variance (burstiness) and token lookup against frequency bins. It is a heuristic statistical analyzer rather than a full transformer logit GLTR tool, but the code is genuine and runs. |
| C12 | "Zero-Assumption Principle: labels unconfirmed breaking events `DATA_VOID`" | README.md L226 | **VERIFIED (RULE-BASED)** | In `src/fusion/truthlens_engine.py` L187-195, if no accredited fact-check match exists and no high CIB anomaly is detected, the engine emits `VerificationVerdict.UNCERTAIN` with explanation `"Data-Void / Pending Corroboration"`. |
| C13 | "Adversarial TextFooler Attack Simulator" | README.md L94 | **REFUTED (HEURISTIC MOCK)** | `src/models/adversarial_tester.py` uses a hard-coded 12-item synonym dictionary (`SYNONYM_REPLACEMENTS`) and character swapping. It does not use semantic embeddings, word saliency rankings, or the real TextAttack framework. |
| C14 | "100% of core algorithms are verified with deterministic automated test suites (`pytest`)" | README.md L230 | **PARTIALLY VERIFIED** | 38 automated unit/integration tests pass. However, they verify heuristic algorithms, schemas, and API contracts—not trained ML models or dataset generalization. |

---

## 3. Required Remediation Strategy

1. **Purge fabricated numbers:** All reported metrics in `docs/` must henceforth cite an exact file path inside `experiments/<run_id>/metrics.json` produced by code executed this session.
2. **Re-implement true baseline & deep learning models:** Replace hard-coded evaluator outputs with real scikit-learn models (TF-IDF + Logistic Regression / Ridge / Naive Bayes), PyTorch deep learning models, and real fine-tuned Transformers.
3. **Download genuine public datasets:** Ingest real public benchmark datasets (LIAR, CoAID, FEVER, ISOT, etc.) with verified checksums.
4. **Relabel simulated components:** Explicitly label mock cascade analysis and heuristic adversarial perturbation as "SIMULATED / HEURISTIC" across docs and codebase until genuinely trained models replace them.
