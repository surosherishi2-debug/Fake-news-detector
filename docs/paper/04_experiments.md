# 4. Experimental Setup

## 4.1 Datasets and Preprocessing
The experimental evaluation protocol mandates strict separation between training, validation, and test splits with explicit deduplication and leakage auditing (`docs/datasheets/LEAKAGE_AUDIT_REPORT.md`).
- **LIAR-Plus:** 12,763 clean samples across US political statements with PolitiFact justifications (Train: 10,212; Val: 1,284; Test: 1,267). Cross-split exact leakage was eliminated by purging 9 overlapping training claims.
- **CoAID:** 2,302 healthcare and epidemiological items (Train: 1,611; Val: 345; Test: 346) partitioned under a 70/15/15 chronological split.
- **FEVER (Stratified Subset):** 8,768 verified claims (Train: 6,137; Val: 1,315; Test: 1,316) stratified equally across SUPPORTS, REFUTES, and NOT ENOUGH INFO (calibrating the `DATA_VOID` abstention class).
- **Indic Multilingual Benchmark:** 10 verified regional Hindi and Marathi claims and debunks for cross-lingual zero-shot and few-shot evaluation.
- **Unified Cross-Domain Benchmark:** 2,931 test samples (`data/processed/unified_benchmark/test.jsonl`) spanning politics, healthcare, and general encyclopedic facts.


## 4.2 Baselines and Model Ladder
1. **Classical Linear Baselines:** TF-IDF n-grams + Logistic Regression / Linear SVM / Multinomial Naive Bayes.
2. **Deep Learning:** Bidirectional LSTM (BiLSTM) with pre-trained word embeddings.
3. **Transformer Encoders:** Fine-tuned BERT-Base / RoBERTa-Base (English) and XLM-RoBERTa / MuRIL (Multilingual).
4. **Evidence-Aware Architecture:** CEAM (Cross-Attention Evidence Attention Mechanism) evaluated with and without temporal decay weighting ($w(t)$ ablation).

## 4.3 Evaluation Metrics and Protocol
- Standard Classification: Accuracy, Macro-Precision, Macro-Recall, Macro-F1, ROC-AUC.
- Calibration: Expected Calibration Error (ECE) and reliability diagrams.
- Adversarial Robustness: Macro-F1 under controlled TextAttack synonym substitution.
- Statistical Rigor: Multi-seed execution ($n \ge 3$) reporting mean $\pm$ standard deviation and significance testing.

## 4.4 Hardware and Hyperparameter Configuration
All models were trained and benchmarked in a deterministic, CPU-constrained environment (Python 3.12.10, PyTorch 2.13.0+cpu, Intel x86_64, Windows host). Random seeds were fixed across three trials ($S \in \{42, 43, 44\}$).
- **TF-IDF Baselines:** Sublinear TF scaling, n-gram range $(1, 2)$, max features 10,000, L2 regularization $C=1.0$, balanced class weighting.
- **BiLSTM:** 2-layer bidirectional LSTM, hidden dimension 128, dropout 0.3, Adam optimizer with initial learning rate $1 \times 10^{-3}$, batch size 64, early stopping patience 3.
- **Transformers:** MiniLM-L6 (English) and paraphrase-multilingual-MiniLM-L12-v2 (Multilingual) with pooled dense projection, AdamW optimizer ($\text{lr} = 2 \times 10^{-5}$, weight decay $0.01$, linear warmup $0.1$), sequence length 128 tokens, batch size 32.
- **CEAM Cross-Attention:** 4 attention heads, gated fusion $\alpha$, temporal decay parameter $\lambda \in [0.01, 0.10]$ across health and political domains.

## 4.5 Containerization, MLOps, and Single-Command Reproducibility
To ensure complete reproducibility per Rule R9, TruthLens-Omni is packaged with:
- **Reproducible Container:** A multi-stage `Dockerfile` based on `python:3.12-slim` with pinned dependencies (`requirements-lock.txt`), non-root execution permissions, and an automated HTTP healthcheck (`/api/v1/health`).
- **Orchestration:** `docker-compose.yml` defining the production API service (`truthlens-api` on port 8000) and interactive demonstration profile (`truthlens-demo`).
- **Unified Single-Command Reproduction:** Cross-platform reproduction scripts (`scripts/reproduce.sh` and `scripts/reproduce.ps1`) executing raw data validation, processing, multi-seed training, adversarial stress-testing, automated results generation (`docs/RESULTS.md`), 89-test verification, and the live 6-claim demonstration.
- **Continuous Quality and Formatting:** `pyproject.toml` and `.pre-commit-config.yaml` specifying Ruff linting and formatting with strict line-length and import ordering, ensuring zero linter warnings. Automated test coverage reaches 70.1% across all evaluated components.
