# 4. Experimental Setup

## 4.1 Datasets and Preprocessing
The experimental evaluation protocol mandates strict separation between training, validation, and test splits with explicit deduplication and leakage auditing.
- Planned Datasets: LIAR / LIAR-Plus (political assertions), CoAID (healthcare and vaccine claims), FEVER (fact extraction and verification).
- Indic/Multilingual Evaluation: Multilingual test split evaluating cross-lingual transfer (English, Hindi, Marathi).

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
