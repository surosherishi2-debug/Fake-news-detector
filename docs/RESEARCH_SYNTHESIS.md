# Research Synthesis & Adopted Architectural Decisions

**Date:** 2026-11-27  
**Phase:** Phase 1 (Literature and Repository Research)  
**Author:** ML/NLP Research Engineer & Architect  
**Purpose:** Synthesize current state-of-the-art literature in misinformation detection, claim verification, and fact-checking; analyze critical industry/academic failure modes; and establish the approved list of datasets and 5 adopted ideas for our ~50% milestone.

---

## 1. State of the Art in Automated Fact Verification (2020–2026)

Research in automated misinformation detection has undergone three distinct evolutionary phases:
1. **Classical Linguistic Classification (2015–2018):** Relied on n-gram statistics, stylistic markers, sensationalist cues, and sentiment polarity using linear classifiers (TF-IDF + Logistic Regression, SVM, Random Forest). These methods capture stylistic clickbait well but fail completely on fact-dense deception disguised in neutral journalistic tone.
2. **Deep Neural & Transformer Encoders (2018–2022):** Fine-tuning BERT, RoBERTa, and DeBERTa on isolated claim texts. While achieving 80–90% in-distribution benchmark accuracy, these models suffer from **surface lexical memorization**: they memorize specific entity tokens and keywords rather than reasoning over factual validity.
3. **Evidence-Conditioned Entailment & Temporal Grounding (2022–2026):** Modern paradigms (FEVER, CheckThat! Lab 2023–2024, TSVer 2025) reframe veracity prediction as a **multi-stage evidence-conditioned retrieval and entailment task**:
   - First, isolate verifiable factual assertions from background opinion (ClaimBuster / CheckThat! Task 1).
   - Second, retrieve contemporary, accredited primary source documents (dense bi-encoders + vector search).
   - Third, assess textual entailment (Supports / Refutes / Not Enough Info) while conditioning on temporal freshness and publisher provenance.

---

## 2. Critical Gaps & Vulnerabilities in Existing Systems

Our survey and audit of the base repository (`docs/REPO_AUDIT.md`) highlighted four critical architectural vulnerabilities in existing systems:

| Gap / Vulnerability | Underlying Mechanism | Empirical Failure Mode | State-of-the-Art Solution |
|---|---|---|---|
| **1. The Adversarial "Text-Only" Collapse** | Text-only models over-index on specific unigram/bigram tokens. | When bad actors substitute synonyms using TextFooler (e.g. swapping "safe" with "riskless"), text-only accuracy drops sharply. | Ground predictions on external immutable ClaimReview citations; cross-attention fuses claim text with external evidence. |
| **2. Temporal Obsolescence** | Real-world factual truth is time-dependent. | An outdated debunk from 3 years ago inappropriately invalidates a legitimate breaking development today. | Apply domain-adaptive exponential temporal decay $w(t) = \exp(-\lambda \Delta t)$ to historical evidence weights. |
| **3. Closed-World Hallucination (Lack of Epistemic Humility)** | Standard classifiers force a softmax decision across [Real, Fake]. | In an empirical "data void" (breaking events with zero verified historical records), models guess with false confidence. | Introduce a first-class `DATA_VOID` / `Unconfirmed` abstention class backed by calibrated probability thresholds. |
| **4. Polarization & Astroturfing Vulnerability** | Raw social media metrics (likes, shares) are easily manipulated by botnet clusters and partisan dogpiling. | Coordinated Inauthentic Behavior (CIB) artificially amplifies false claims to game popularity algorithms. | Implement decentralized bipartisan matrix factorization (Community Notes algorithm) to reward cross-ideological agreement. |

---

## 3. The 5 Core Adopted Ideas (With Citations & Implementation Mapping)

Based on our empirical survey and source verification, we formally adopt the following 5 architectural and methodological pillars:

### [Idea 1] Evidence-Conditioned Veracity Modeling with Calibrated Abstention
- **Published Foundation:** Thorne et al. (NAACL 2018; FEVER), Alhindi et al. (EMNLP 2018; LIAR-Plus), CLEF CheckThat! Lab (2024).
- **Description:** Rather than predicting truthfulness from isolated article text, veracity is determined by conditioned cross-attention between the claim $Q$ and retrieved evidence $K, V$. The model outputs a calibrated tripartite distribution:
  1. `VERIFIED` (Evidence corroborates factual assertions)
  2. `REFUTED` (Evidence contradicts assertions)
  3. `DATA_VOID` (Evidence is insufficient; the system strictly abstains from guessing)
- **Why Adopted:** Eliminates closed-world hallucinations on breaking news and forces the system to provide an explainable citation trail for every verdict.
- **Target Phase:** Phase 2 (Data preparation) & Phase 3 (Model ladder).

---

### [Idea 2] Domain-Adaptive Exponential Temporal Evidence Decay ($w(t)$)
- **Published Foundation:** Quantemp (IJCAI 2024), TSVer (ACL 2025), TruthLens formulation.
- **Description:** Retrieved evidence documents are modulated by their temporal offset $\Delta t = |t_{\text{claim}} - t_{\text{evidence}}|$ in years:
  $$w(t) = \exp(-\lambda \cdot \Delta t)$$
  with domain-adaptive decay rates reflecting epistemic turnover:
  - $\lambda_{\text{politics}} = 0.35$ (Half-life $\approx 2$ years; political claims obsolesce rapidly)
  - $\lambda_{\text{health}} = 0.10$ (Half-life $\approx 7$ years; medical consensus evolves moderately)
  - $\lambda_{\text{science}} = 0.01$ (Half-life $\approx 70$ years; foundational physical sciences persist)
- **Why Adopted:** Prevents temporal obsolescence without discarding historical archives. We will measure its exact contribution via an ablation study in Phase 3 ($w(t)$ enabled vs. disabled).
- **Target Phase:** Phase 3 (Ablation study) & Phase 4 (Retrieval weighting).

---

### [Idea 3] Two-Stage Dense Semantic Retrieval Pipeline
- **Published Foundation:** Reimers & Gurevych (EMNLP 2019; Sentence-BERT), Karpukhin et al. (EMNLP 2020; Dense Passage Retrieval).
- **Description:** Replace the fragile 3-item hard-coded keyword matching in `src/retrieval/fact_check_client.py` with a two-stage retrieval architecture:
  1. **Stage 1 (Bi-Encoder Dense Indexing):** Pre-embed curated ClaimReview evidence using `sentence-transformers/all-MiniLM-L6-v2` with cosine similarity retrieval.
  2. **Stage 2 (Cross-Encoder Re-Ranking):** Re-rank top-$k$ candidate evidence snippets against the atomic claim assertion to select the top 3 most relevant sentences.
- **Why Adopted:** Scalable, offline-capable, and immune to superficial keyword mismatches while integrating cleanly with our local SQLite store.
- **Target Phase:** Phase 4 (Retrieval & Explainability).

---

### [Idea 4] Adversarial Stress Testing Protocol via TextAttack
- **Published Foundation:** Jin et al. (AAAI 2020; TextFooler), Morris et al. (EMNLP 2020; TextAttack).
- **Description:** Replace the base repo's hard-coded 12-word dictionary simulator with genuine TextAttack adversarial recipes:
  - **TextFooler:** Semantic-preserving synonym substitutions using cosine similarity in counter-fitted embedding space with POS constraints.
  - **DeepWordBug:** Character-level typo/swap perturbation to test subword tokenizer robustness.
- **Evaluation Metric:** Measure both Clean Macro-F1 and Adversarial Macro-F1, computing the **Robustness Retention Ratio**:
  $$\text{Robustness Ratio} = \frac{\text{Macro-F1}_{\text{adversarial}}}{\text{Macro-F1}_{\text{clean}}}$$
- **Why Adopted:** Replaces fabricated README numbers with real, reproducible adversarial benchmark curves produced by verified libraries.
- **Target Phase:** Phase 3 (Model evaluation).

---

### [Idea 5] Multilingual Indic Vernacular Transfer via Google MuRIL & XLM-RoBERTa
- **Published Foundation:** Khanuja et al. (2021; MuRIL), Conneau et al. (ACL 2020; XLM-RoBERTa).
- **Description:** Fine-tune multilingual encoders on a curated tripartite language split: English, Hindi, and Marathi. Benchmark cross-lingual zero-shot and few-shot transfer across languages.
- **Why Adopted:** The base repo claimed native Marathi and Hindi performance on `PuneFakeNews-2024`, but only contained 8 mock samples. Utilizing `google/muril-base-cased` (Apache 2.0) and genuine Indic fact-checks enables a true regional evaluation.
- **Target Phase:** Phase 3 (Multilingual model ladder).

---

## 4. Approved Candidate Dataset Portfolio (For Phase 2)

We propose the following 4 distinct, verified benchmark datasets for download, versioning, and preprocessing in Phase 2:

| Dataset | Domain | Size / Scope | Label Scheme | Source / License | Verified Access |
|---|---|---|---|---|---|
| **1. LIAR-Plus** | Politics & Government | 12,836 statements with extracted justifications | 6-way veracity (*pants-fire, false, mostly-false, half-true, mostly-true, true*) | `Tariq60/LIAR-PLUS` (CC BY-NC 4.0) | Verified raw TSV download |
| **2. CoAID** | Healthcare & COVID-19 | 4,251 articles/claims with fact-check citations | Binary (*Real, Fake*) + user engagements | `cuilimeng/CoAID` (Academic Open Source) | Verified raw CSV download |
| **3. FEVER (Subset)** | General Factoid & Wikipedia | 10,000 stratified claim-evidence pairs | Tripartite (*SUPPORTS, REFUTES, NOT ENOUGH INFO*) | `fever.ai` (CC BY-SA 4.0) | Verified raw JSONL download |
| **4. Indic Multilingual Benchmark** | Regional Indic (Hindi & Marathi) | Curated multi-domain claims and IFCN fact-checks | Binary / Tripartite | Scraped IFCN / PIB / BoomLive archive | Open public debunks |
