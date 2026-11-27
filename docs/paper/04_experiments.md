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

```
[TODO/UNVERIFIED]
- Hardware specifications, training hyperparameters, learning rates, batch sizes, and optimizer schedules to be recorded upon Phase 3 execution in experiments/ configs.
```
