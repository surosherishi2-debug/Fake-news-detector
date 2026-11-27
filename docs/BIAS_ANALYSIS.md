# Subgroup Disparity & Bias Analysis (BIAS_ANALYSIS.md)

**Project:** TruthLens-Omni  
**Scope:** Phase 7 Responsible AI Evaluation  
**Evaluation Benchmark:** Unified Cross-Domain Benchmark (2,931 test samples) across Seeds [42, 43, 44]  

---

## 1. Executive Summary
Misinformation detection systems frequently exhibit systematic performance disparities across topical domains, language families, and syntactic writing styles. In accordance with Rule R1 (No Assumptions) and R2 (No Fabricated Numbers), this audit measures empirical disparities across three critical dimensions:
1. **Topical Disparity:** Political discourse vs. Biomedical/Epidemiological facts vs. Encyclopedic assertions.
2. **Linguistic & Cultural Disparity:** High-resource English vs. Low-resource Indic languages (Hindi, Marathi).
3. **Structural Complexity:** Short lexical headlines vs. Multi-clause sentences with embedded negation.

---

## 2. Topical Performance Disparity

Performance was stratified across the three primary source datasets composing the Unified Benchmark:

| Topical Domain | Source Dataset | Test Samples | Baseline F1 (LR) | Transformer F1 (MiniLM) | CEAM F1 (+Temporal) | Primary Error Mode |
|---|---|---|---|---|---|---|
| **Health / Biomedical** | CoAID | 346 | **68.42%** | **74.18%** | 61.20% | Domain Lexical Drift (11.4%) |
| **Political Discourse** | LIAR-Plus | 1,267 | 51.20% | 55.40% | 38.80% | Numerical Distortions (28.6%) |
| **General / Encyclopedic** | FEVER | 1,316 | 49.80% | 53.60% | 34.40% | Data-Void Uncertainty (22.9%) |

### Findings & Root Causes:
1. **Biomedical Superiority (+18.78% F1):** Healthcare misinformation exhibits tight semantic clustering around accredited clinical entities (e.g. "CDC", "FDA", "vaccine", "clinical trial"). The retrieved evidence achieves high cosine similarity ($\ge 0.65$), yielding strong verification confidence.
2. **Political Nuance Deficit:** Political claims suffer from high rhetorical spin, selective metric quoting, and ideological framing. Models frequently over-index on political party names rather than verifying the underlying economic or legislative claims.
3. **General Domain Data Voids:** FEVER's stratified `NOT ENOUGH INFO` class highlighted the essential role of calibrated abstention: without the $\tau = 0.40$ threshold, classifiers attempted to guess truth on 438 unverifiable claims.

---

## 3. Cross-Lingual & Cultural Disparity

| Language Family | Subgroup | Samples | Multilingual MiniLM Acc | Indic Zero-Shot Transfer Acc | Error Risk Profile |
|---|---|---|---|---|---|
| **High-Resource Germanic** | English (en) | 2,921 | 58.79% | N/A | Balanced across all classes |
| **Indo-Aryan (Devanagari)** | Hindi (hi) | 6 | 100.0% (sample) | 100.0% | Dialectal colloquialisms |
| **Indo-Aryan (Devanagari)** | Marathi (mr) | 4 | 100.0% (sample) | 100.0% | Morphological agglutination |

### Critical Observations:
- **Zero-Shot Dense Transfer:** The multilingual encoder (`paraphrase-multilingual-MiniLM-L12-v2`) project English claims and regional Devanagari fact-checks into a shared 384-dimensional metric space. The Marathi regional cyber-crime claim ("पुणे सायबर पोलिसांनी नवीन डिजिटल अटक नियम जारी केले आहेत") successfully aligned with its regional debunk ($S_{dense} = 0.58$) without language-specific translation pipelines.
- **Sample Size Warning (R1 Compliance):** The Indic test set currently contains 10 verified samples. While 100% accuracy was recorded on this set, it cannot be generalized to broader colloquial Hindi/Marathi social media text without expanding the benchmark to $\ge 500$ samples in production Phase 8.

---

## 4. Syntactic Complexity & Negation Sensitivity

Failure mode analysis across 35 concrete model errors (`docs/ERROR_ANALYSIS.md`) demonstrated severe sensitivity to sentence length and syntactic polarity:

| Claim Characteristic | Error Proportion | Manifested Vulnerability |
|---|---|---|
| **Short Claims (< 15 tokens)** | 22.8% | Over-reliance on solitary unigrams; shallow keyword matching. |
| **Long Multi-Clause Claims (> 35 tokens)** | 31.4% | Context dilution in fixed-window tokenizers; loss of modifier scope. |
| **Syntactic Negation ("never", "failed to")** | 14.3% | Polarity inversion: model predicts `VERIFIED` when evidence states `NOT TRUE`. |
| **Numerical Assertions (rates, percentages)** | 28.6% | Arithmetic blindness: model treats "decreased by 10%" as confirming "decreased by 90%". |

---

## 5. Mitigation Strategies Implemented in TruthLens-Omni

1. **Syntactic Polarity Pre-Flight:** `PreflightAuditor` scans claims for negative polarity tokens and flags potential double negatives before classification.
2. **Calibrated Epistemic Abstention:** Rather than forcing a high-error guess on sparse political or encyclopedic claims, the retriever enforces an epistemic floor ($\tau = 0.40$).
3. **FDA-Style Epistemic Nutrition Card:** All outputs display the multi-dimensional breakdown (Source Authority, Fact-Check Citation, Stance Consensus, and Token Attribution), ensuring users never consume an opaque black-box probability.
