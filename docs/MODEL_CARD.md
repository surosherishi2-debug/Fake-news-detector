# TruthLens-Omni: Model Card

Following the Model Cards for Model Reporting framework (Mitchell et al., 2019).

---

## 1. Model Details
- **Model Name:** TruthLens-Omni Epistemic Verification Engine
- **Version:** 1.0.0 (~50% Milestone Benchmark Checkpoint)
- **Model Architecture:** Tripartite hybrid architecture:
  1. *Classical Linear Baselines:* Sublinear TF-IDF + Logistic Regression / Linear SVM / Multinomial Naive Bayes.
  2. *Deep Recurrent Classifier:* 2-layer Bidirectional LSTM (BiLSTM) with word embeddings.
  3. *Dense Semantic Transformer:* Fine-tuned English `sentence-transformers/all-MiniLM-L6-v2` and Multilingual `paraphrase-multilingual-MiniLM-L12-v2` (384-dimensional dense semantic projections).
  4. *Cross-Attention Evidence Mechanism (CEAM):* Gated cross-attention with domain-adaptive exponential temporal decay $w(t) = \exp(-\lambda \Delta t)$.
- **License:** MIT License
- **Developed By:** TruthLens-Omni Research & Engineering Team
- **Release Date:** November 2026

---

## 2. Intended Use
### 2.1 Primary Intended Uses
- **Assisted Fact-Checking:** Augmenting professional journalists, intelligence analysts, and researchers by decomposing complex statements into atomic factual assertions and retrieving contemporary accredited fact-checks.
- **Epistemic Nutrition Assessment:** Providing transparent, multi-dimensional veracity cards displaying source authority, temporal distance, stance classification, and token-level saliency.
- **Calibrated Abstention:** Refusing to render a definitive real/fake verdict on claims lacking external evidence (`DATA_VOID` status), thereby preventing generative hallucination.

### 2.2 Out-of-Scope and Prohibited Uses
- **Autonomous Censorship:** TruthLens-Omni must NEVER be deployed as a fully autonomous censorship engine or content takedown system without human-in-the-loop editorial review.
- **Subjective & Opinion Evaluation:** Not designed to evaluate pure subjective commentary, political satire, aesthetic judgments, or religious/theological beliefs.
- **Punitive Action:** Prohibited from being used as sole justification for punitive legal, institutional, or account-suspension actions.

---

## 3. Training & Evaluation Data
All training and evaluation data adhere to strict deduplication and anti-leakage protocols (`data/checksums.sha256`, `docs/datasheets/LEAKAGE_AUDIT_REPORT.md`):

| Dataset | Domain | Primary Language | Split (Train / Val / Test) | Source / Reference |
|---|---|---|---|---|
| **LIAR-Plus** | Political discourse | English | 10,212 / 1,284 / 1,267 | Wang (2017), Alhindi et al. (2018) |
| **CoAID** | Health & COVID-19 | English | 1,611 / 345 / 346 | Cui & Lee (2020) |
| **FEVER (Stratified)** | Encyclopedic & General | English | 6,137 / 1,315 / 1,316 | Thorne et al. (2018) |
| **Indic Benchmark** | Regional Fact-Checks | Hindi, Marathi | 6 / 2 / 2 | Verified IFCN / BOOM / Vishwas News |
| **Unified Test Suite** | Balanced Cross-Domain | Multilingual | 2,931 test samples | Unified evaluated benchmark |

Cross-split leakage elimination: 9 verbatim overlapping claims were actively detected and purged from the training split.

---

## 4. Quantitative Performance Summary

Master benchmark metrics measured across fixed seeds ($S \in \{42, 43, 44\}$) on the 2,931-sample Unified Benchmark (`docs/RESULTS.md`):

| Model Ladder Tier | Test Accuracy | Macro-Precision | Macro-Recall | Macro-F1 | ROC-AUC | Adversarial Retention |
|---|---|---|---|---|---|---|
| **TF-IDF + Naive Bayes** | 53.97% | 46.54% | 52.88% | 44.89% | 0.7029 | 91.24% |
| **TF-IDF + Linear SVM** | 56.06% | 51.56% | 49.33% | 49.88% | 0.7018 | 92.40% |
| **TF-IDF + Logistic Regression** | 58.34% | 53.86% | 51.49% | 51.83% | 0.7495 | 93.85% |
| **BiLSTM (2-layer)** | 57.83% | 55.62% | 53.25% | 54.10% | 0.7321 | 92.15% |
| **Multilingual MiniLM-L12** | 58.79% | 54.80% | 53.79% | 54.05% | 0.7642 | 95.80% |
| **English MiniLM-L6 (Best)** | **59.84%** | **56.12%** | **55.03%** | **55.17%** | **0.7802** | **96.17%** |
| **CEAM (+Temporal Decay)** | 54.55% | 50.15% | 45.35% | 36.16% | 0.6840 | 94.10% |
| **CEAM (-Temporal Decay)** | 58.27% | 54.91% | 48.74% | 40.39% | 0.7188 | 94.62% |

*Note on Honest Scope:* The social cascade graph module (`HeteroGraphEncoder` / `CascadeTopologyAnalyzer`) is labeled as `[SIMULATED DEMO]` per Decision D13 and is excluded from headline model metrics.

---

## 5. Environmental & Computational Footprint
- **Hardware Used:** Intel Core i7 / x86_64 CPU (8 physical cores, 16 threads). No GPU acceleration was required or utilized.
- **Operating System:** Windows 11 Enterprise (Python 3.12.10).
- **Total Training & Evaluation Compute:** ~4.2 CPU hours across all seeds, model ladder runs, and adversarial sweeps.
- **Estimated Energy Consumption:** ~0.25 kWh.
- **Estimated Carbon Emissions:** $\approx 0.10 \text{ kg CO}_2\text{e}$ (based on global average grid carbon intensity of 400 g $\text{CO}_2$/kWh).

---

## 6. Ethical Considerations & Risk Mitigation
1. **False Positive Reputational Harm:** Mislabeling true assertions as fake can delegitimize factual journalism. TruthLens-Omni mitigates this by computing token saliency and highlighting exact evidence sentences that contradict the claim.
2. **Data-Void Exploitation:** During early-stage viral rumors, lack of evidence could be mistaken for confirmation. The system enforces strict epistemic abstention ($\tau = 0.40$ threshold): claims with dense similarity $< 0.40$ return `DATA_VOID / UNCERTAIN` with confidence 0.0.
3. **Linguistic Equity:** To prevent neglect of non-English populations, the architecture operates over a shared 384-dimensional multilingual vector space, successfully verifying Marathi and Hindi fact-checks without language-specific translation.
