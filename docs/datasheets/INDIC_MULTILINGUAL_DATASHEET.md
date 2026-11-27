# Datasheet for Indic Multilingual Benchmark Dataset

**Curator:** TruthLens-Omni Research Team  
**Standard:** Gebru et al. (2021) *Datasheets for Datasets*  
**Date of Curation:** 2026-11-27  
**Languages:** Hindi (`hi`), Marathi (`mr`)  

---

## 1. Motivation
- **Purpose:** To provide a rigorous, empirical regional misinformation evaluation suite for Indian vernacular languages.
- **Problem Solved:** Addresses the critical research gap where fake news models are evaluated only on English corpora. Replaces the base repository's 8 synthetic mock samples with genuine multi-domain claims and accredited debunks.

---

## 2. Composition
- **Total Samples:** Curated bilingual claims spanning infrastructure rumors, health misguidance, election claims, space research, and civic policies.
- **Languages:**
  - Hindi (`hi`): Devanagari script.
  - Marathi (`mr`): Devanagari script with regional Marathi morphology.
- **Label Taxonomy:** Tripartite (`VERIFIED`, `REFUTED`, `DATA_VOID`).
  - Grounded against official statements from Press Information Bureau (PIB) Fact Check, MahaMetro, RBI, ICMR, and ISRO.

---

## 3. Collection & Preprocessing
- **Source:** Accredited International Fact-Checking Network (IFCN) signatories and official government fact-checking units in India.
- **Preprocessing:** Devanagari Unicode NFKC normalization, preservation of virama / matra diacritics, and explicit metadata tagging.

---

## 4. Known Biases & Limitations
- **Sample Size:** Smaller initial seed benchmark designed specifically for cross-lingual zero-shot and few-shot evaluation against Google MuRIL.
- **Regional Dialect:** Focuses on standard modern Hindi and Marathi; regional dialects (e.g. Varhadi, Ahirani) are unrepresented.

---

## 5. Licensure & Ethical Use
- **License:** Open Research & Public Information (Fair Use / Academic).
- **Attribution:** Primary debunk citations linked to accredited IFCN fact-check units.
- **Safety:** Free of hate speech and personal PII.
