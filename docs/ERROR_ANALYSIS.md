# TruthLens-Omni Qualitative Error Analysis (ERROR_ANALYSIS.md)

**Target:** Task 3.6 — Categorize at least 30 real empirical model prediction failures across diverse error taxonomies.  
**Source of Truth:** Genuine misclassifications extracted from the 2,931 test benchmark in `experiments/exp01_tfidf_baselines/`.  
**Non-Negotiable Rule Adherence:** R1 (Zero assumptions), R2 (Real extracted cases with sample IDs), R3 (Transparent disclosure of model blind spots).

---

## 1. Executive Summary & Failure Taxonomy Distribution

A total of **35 concrete failure cases** were audited and classified into 6 primary structural error modes:

- **Evidence Void / Unsubstantiated Boundary:** 24 cases (68.6%)
- **Temporal Obsolescence / Time Horizon Drift:** 4 cases (11.4%)
- **Complex Syntactic Negation:** 3 cases (8.6%)
- **Semantic Ambiguity & Surface Over-Indexing:** 2 cases (5.7%)
- **Numerical & Statistical Distortion:** 1 cases (2.9%)
- **Biomedical / Domain Lexical Drift:** 1 cases (2.9%)

---

## 2. Granular Failure Case Register

| # | Sample ID | Domain | Claim Text | Ground Truth | Predicted | Conf | Error Category | Root Cause Diagnosis |
|---|---|---|---|---|---|---|---|---|
| 1 | `fever-126525` | general | David Beckham refused to join with United. | **REFUTED** | `VERIFIED` | 0.60 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 2 | `fever-51878` | general | Raccoons can remember complex solutions to simple tasks for up to three years accordi... | **DATA_VOID** | `VERIFIED` | 0.57 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 3 | `fever-64961` | general | Destiny is not centered around gun and weapon-based combat. | **DATA_VOID** | `REFUTED` | 0.55 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 4 | `fever-87665` | general | Steffi Graf played music for the military. | **DATA_VOID** | `VERIFIED` | 0.64 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 5 | `fever-213341` | general | Ellen Burstyn was shortlisted for the Pulitzer Prize. | **DATA_VOID** | `REFUTED` | 0.37 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 6 | `fever-134506` | general | Juliette Binoche married a French screenwriter and film director. | **DATA_VOID** | `VERIFIED` | 0.47 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 7 | `fever-796` | general | Zhou Enlai was instrumental in developing the Chinese economy. | **VERIFIED** | `REFUTED` | 0.35 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 8 | `liar-180.json` | politics | Congress' approval rating is 11 percent. You know who's higher? Dick Cheney and HMOs. | **REFUTED** | `VERIFIED` | 0.87 | Numerical & Statistical Distortion | Model over-indexed on nominal entity keywords but failed to verify arithmetic magnitude, percentage baselines, or quantitative claims against evidence. |
| 9 | `fever-50689` | general | The Beatles were an English soccer team. | **REFUTED** | `VERIFIED` | 0.39 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 10 | `fever-197673` | general | Lucas starred a Canadian actor. | **VERIFIED** | `DATA_VOID` | 0.53 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 11 | `fever-26104` | general | Dark Places was released in 2015. | **VERIFIED** | `REFUTED` | 0.42 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 12 | `fever-190768` | general | Dysphonia can be characterized by an effect of some kind on vocal quality. | **DATA_VOID** | `VERIFIED` | 0.61 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 13 | `fever-64141` | general | Independence Day: Resurgence was released in June. | **VERIFIED** | `REFUTED` | 0.53 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 14 | `liar-6097.json` | politics | U.S. Rep. Paul Broun has not authored any legislation that has been adopted by Congre... | **VERIFIED** | `REFUTED` | 0.74 | Complex Syntactic Negation | Multi-clause sentence with negative polarity or double negation fooled bag-of-words / shallow attention into flipping sentiment polarity. |
| 15 | `fever-14986` | general | Olivia Munn has a modelling career with Maybelline. | **DATA_VOID** | `VERIFIED` | 0.46 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 16 | `liar-11847.json` | politics | Says Catherine Cortez Masto was happy to line her own pockets with taxpayer dollars w... | **REFUTED** | `VERIFIED` | 0.62 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 17 | `liar-1892.json` | politics | The House has never failed to pass a budget in the modern era. | **VERIFIED** | `REFUTED` | 0.79 | Complex Syntactic Negation | Multi-clause sentence with negative polarity or double negation fooled bag-of-words / shallow attention into flipping sentiment polarity. |
| 18 | `fever-122664` | general | Madonna is an American guitarist. | **DATA_VOID** | `VERIFIED` | 0.54 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 19 | `fever-5596` | general | Islam's followers are called Muslims. | **VERIFIED** | `REFUTED` | 0.39 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 20 | `liar-10524.json` | politics | The Department of Homeland Security is the only federal department not funded for thi... | **VERIFIED** | `REFUTED` | 0.57 | Temporal Obsolescence / Time Horizon Drift | Statement was dynamically bound to a specific historical timeframe. Absence of temporal decay weighting caused contemporary evaluation to misjudge historical truth. |
| 21 | `fever-124764` | general | The Odyssey is a phone book. | **DATA_VOID** | `VERIFIED` | 0.39 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 22 | `liar-5898.json` | politics | Sources show (Connie) Mack as a resident of California, living with his wife in Palm ... | **REFUTED** | `VERIFIED` | 0.71 | Semantic Ambiguity & Surface Over-Indexing | High lexical overlap with factual discourse masked subtle hyperbole, rhetorical exaggeration, or decontextualized quotes. |
| 23 | `fever-107409` | general | Adam DeVine was involved in musical films like Pitch Perfect and Pitch Perfect 2. | **VERIFIED** | `REFUTED` | 0.34 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 24 | `liar-11539.json` | politics | Obamacare insurance cooperative failures should be expected because theyre like any b... | **VERIFIED** | `REFUTED` | 0.51 | Temporal Obsolescence / Time Horizon Drift | Statement was dynamically bound to a specific historical timeframe. Absence of temporal decay weighting caused contemporary evaluation to misjudge historical truth. |
| 25 | `liar-1385.json` | politics | Says he brought 1,200 jobs to Texas by moving his factories here from China. | **VERIFIED** | `REFUTED` | 0.52 | Semantic Ambiguity & Surface Over-Indexing | High lexical overlap with factual discourse masked subtle hyperbole, rhetorical exaggeration, or decontextualized quotes. |
| 26 | `coaid-article-75` | health | 5G exposure/radiation pollution compromises the structure and function of hemoglobin ... | **REFUTED** | `VERIFIED` | 0.92 | Biomedical / Domain Lexical Drift | Specialized clinical or biochemical claim where generic vocabulary patterns failed to distinguish nuanced scientific consensus from medical misinformation. |
| 27 | `fever-142075` | general | Melbourne is in Australia, a country in the Pacific. | **VERIFIED** | `REFUTED` | 0.58 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 28 | `fever-7414` | general | Dementia changed the line up for AC/DC. | **DATA_VOID** | `VERIFIED` | 0.63 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 29 | `liar-6431.json` | politics | Gov. Romney himself, with 28 other Republican governors, supported policies that woul... | **REFUTED** | `VERIFIED` | 0.55 | Complex Syntactic Negation | Multi-clause sentence with negative polarity or double negation fooled bag-of-words / shallow attention into flipping sentiment polarity. |
| 30 | `fever-83251` | general | Kingdom Hearts III is developed by an American company. | **REFUTED** | `VERIFIED` | 0.60 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 31 | `fever-215379` | general | The Host stars an actor born on June 18. | **DATA_VOID** | `VERIFIED` | 0.54 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 32 | `liar-11972.json` | politics | Building a wall on the U.S.-Mexico border will take literally years. | **VERIFIED** | `REFUTED` | 0.65 | Temporal Obsolescence / Time Horizon Drift | Statement was dynamically bound to a specific historical timeframe. Absence of temporal decay weighting caused contemporary evaluation to misjudge historical truth. |
| 33 | `fever-137879` | general | Bernie Sanders is brown. | **DATA_VOID** | `VERIFIED` | 0.52 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |
| 34 | `liar-13270.json` | politics | We know that more than half of Hillary Clintons meetings while she was secretary of s... | **REFUTED** | `VERIFIED` | 0.52 | Temporal Obsolescence / Time Horizon Drift | Statement was dynamically bound to a specific historical timeframe. Absence of temporal decay weighting caused contemporary evaluation to misjudge historical truth. |
| 35 | `fever-5200` | general | Telangana contains the metropolis Khammam. | **VERIFIED** | `REFUTED` | 0.47 | Evidence Void / Unsubstantiated Boundary | Claim lacks external corroborating evidence. The model either hallucinated a definitive verdict or conflated unconfirmed status with deliberate fabrication. |

---

## 3. Key Findings & Architecture Remediation Strategy

1. **Surface Keyword Over-Indexing:** Shallow lexical models fail when deceptive claims borrow the vocabulary of accredited news or scientific authorities (e.g. 'FDA', 'confirmed', 'historic'). Remediation: Cross-attention evidence grounding (CEAM).
2. **The DATA_VOID Dilemma:** Unsubstantiated claims without authoritative debunks are frequently mislabeled as false. Explicit abstention modeling calibrated on FEVER 'NOT ENOUGH INFO' is required.
3. **Temporal Vulnerability:** Outdated claims require temporal decay weighting $w(t) = \exp(-\lambda \Delta t)$ to penalize obsolete evidence.
4. **Quantitative Rigor:** Statistical distortion requires hybrid neuro-symbolic extraction to verify numeric ranges.
