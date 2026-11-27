# Datasheet for CoAID Healthcare Misinformation Dataset

**Authors:** Limeng Cui and Dongwon Lee (Penn State University)  
**Publication:** *CoAID: COVID-19 Healthcare Misinformation Dataset* (arXiv:2006.00885, 2020)  
**Standard:** Gebru et al. (2021) *Datasheets for Datasets*  
**Date of Curation:** 2026-11-27  

---

## 1. Motivation
- **Purpose:** Created to provide an empirical healthcare and epidemiological misinformation benchmark during the early phases of the COVID-19 pandemic.
- **Problem Solved:** Misinformation in healthcare carries life-or-death consequences. CoAID provides verified true news articles alongside debunked conspiracy claims and unverified rumors across social media.

---

## 2. Composition
- **Total Samples:** 4,251 claim and news items with associated social platform engagements.
- **Categories:**
  - `ClaimFakeCOVID-19.csv` (Debunked claims from accredited fact-checkers)
  - `ClaimRealCOVID-19.csv` (Verified public health claims from WHO/CDC)
  - `NewsFakeCOVID-19.csv` (Full-length false news stories)
  - `NewsRealCOVID-19.csv` (Full-length verified medical releases)
- **Label Scheme:** Binary (*Real, Fake*) mapped to TruthLens tripartite ontology:
  - Fake Claims & News $\to$ **`REFUTED`**
  - Real Claims & News $\to$ **`VERIFIED`**

---

## 3. Collection & Preprocessing
- **Source:** Reliable institutional portals (WHO, CDC, NIH) and accredited fact-checking organizations (PolitiFact, FactCheck.org, Lead Stories).
- **Preprocessing:** Cleaned article titles and claims, removal of dead URLs, and deduplication of near-identical viral headlines.

---

## 4. Known Biases & Limitations
- **Topic Concentration:** Exclusively COVID-19 epidemiology, virology, clinical symptoms, and vaccine efficacy.
- **Temporal Window:** Collected primarily during the first half of 2020. Scientific knowledge regarding treatments evolved substantially following this period, making this an ideal testbed for temporal decay analysis.

---

## 5. Licensure & Ethical Use
- **License:** Open Academic Research Use (`cuilimeng/CoAID`).
- **Attribution:** Cite Cui and Lee (2020).
- **Safety:** Contains no patient medical records or private health information (PHI).
