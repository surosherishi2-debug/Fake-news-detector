# Datasheet for LIAR-PLUS Benchmark Dataset

**Authors:** Tariq Alhindi, Rishita Chakravarti, Smaranda Muresan (Columbia University)  
**Publication:** *Where is your Evidence: Improving Fact-checking by Justification Modeling* (EMNLP 2018 Workshop on FEVER)  
**Standard:** Gebru et al. (2021) *Datasheets for Datasets*  
**Date of Curation:** 2026-11-27  

---

## 1. Motivation
- **Purpose:** Created to evaluate automated fact-checking models on real-world political claims where claims are accompanied by human-extracted justification summaries.
- **Problem Solved:** While the original LIAR dataset (Wang, 2017) contained short political statements with veracity labels, it lacked grounded evidence. LIAR-Plus automatically extracts the justification paragraphs written by professional PolitiFact journalists to support their rulings.

---

## 2. Composition
- **Total Samples:** ~12,836 statements across train, validation, and test splits.
  - Train: 10,240 records (`train2.tsv`)
  - Validation: 1,284 records (`val2.tsv`)
  - Test: 1,267 records (`test2.tsv`)
- **Input Modality:** Text (Statements, Speaker metadata, Context, Justification evidence).
- **Label Taxonomy (Raw):** 6-way fine-grained veracity:
  1. `pants-fire` (Severe fabrication)
  2. `false` (Refuted assertion)
  3. `barely-true` (Substantially misleading)
  4. `half-true` (Mixed veracity)
  5. `mostly-true` (Accurate with minor omissions)
  6. `true` (Completely verified)
- **Label Mapping for TruthLens:**
  - `pants-fire`, `false`, `barely-true` $\to$ **`REFUTED`**
  - `half-true`, `mostly-true`, `true` $\to$ **`VERIFIED`**

---

## 3. Collection & Preprocessing
- **Source:** PolitiFact.com (US politics, federal legislation, presidential speeches).
- **Collection Method:** Web scraping of PolitiFact rulings paired with regex extraction of the concluding "Our Ruling" justification text.
- **Normalization:** Unicode NFKC normalization, whitespace collapsing, tab separation parsing.

---

## 4. Known Biases & Limitations
- **Political Domain Skew:** 100% focused on US domestic politics. Linguistic style is predominantly political speeches, press releases, and televised debates.
- **Temporal Skew:** Statements originate primarily from 2007 to 2016.
- **Speaker Imbalance:** Disproportionate concentration of high-profile political figures (e.g. Barack Obama, Donald Trump, Mitt Romney).

---

## 5. Licensure & Ethical Use
- **License:** Open Research / Academic License (CC BY-NC 4.0).
- **Attribution:** Cite Wang (ACL 2017) and Alhindi et al. (EMNLP 2018).
- **PII:** Contains names of public political figures speaking in their official capacity; no private personal data.
