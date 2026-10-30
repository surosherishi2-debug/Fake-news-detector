# TruthLens-Omni: Phase 6 Implementation Plan & Architectural Review

**Document Version**: 2.0.0  
**Target Release**: TruthLens-Omni Enterprise & Capstone Edition  
**Repository**: [Fake-news-detector](https://github.com/surosherishi2-debug/Fake-news-detector)  
**Live Cloud Deployment**: [https://truthlens-omni.onrender.com](https://truthlens-omni.onrender.com)  

---

## 1. Executive Summary & Implementation Strategy (In Brief)

This plan elevates **TruthLens-Omni** from an academic prototype into a production-grade epistemic intelligence platform across 4 focused implementation waves:

```
[Wave 1: Visual Highlighting & Adaptive Decay]
       │
       ▼
[Wave 2: GLTR Token Heatmap & Visual Entropy]
       │
       ▼
[Wave 3: Knowledge Graph Chrono-Slider & Clusters]
       │
       ▼
[Wave 4: Authoring Citation Assistant & Multi-Attack Suite]
```

### Core Implementation Principles
1. **Zero-Regression Principle**: All changes maintain backward compatibility with the existing FastAPI endpoints and the live Render cloud deployment.
2. **Lightweight Edge Constraint**: Zero heavy CUDA/PyTorch runtime additions; all vector operations leverage NumPy and optimized mathematical algorithms to keep RAM usage < 150MB on Render's 512MB free tier.
3. **Finnova Design Cohesion**: All new interactive visualizers adhere strictly to the 8-point spatial grid, dark obsidian surfaces (`#151624`), and high-contrast typography.

---

## 2. Wave-by-Wave Atomic Task Breakdown

### Wave 1: Visual Sentence-Level Truth Highlighting & Domain-Adaptive Decay
- **Task 1.1: Domain-Adaptive Temporal Decay ($\lambda_d$)**
  - *Backend*: Extend `src/core/temporal.py` and `src/fusion/truthlens_engine.py` with domain-specific half-life calibration:
    - Breaking Politics: $\lambda = 0.35$ ($t_{1/2} \approx 2$ days).
    - Public Health: $\lambda = 0.10$ ($t_{1/2} \approx 7$ days).
    - Science & Space: $\lambda = 0.01$ ($t_{1/2} \approx 70$ days).
- **Task 1.2: Sentence-Level Inline Text Highlighting**
  - *Frontend*: In `src/web/static/js/app.js` and `index.html`, add an interactive **"Annotated Story Reader"** to the Deep Fact Checker.
  - Sentences are wrapped in interactive spans:
    - 🟢 Green (`bg-emerald-500/15 border-b-2 border-emerald-500 text-emerald-200`): Empirically verified assertions.
    - 🔴 Red (`bg-rose-500/15 border-b-2 border-rose-500 text-rose-200`): Refuted / fabricated statements.
    - 🟡 Amber (`bg-amber-500/15 border-b-2 border-amber-500 text-amber-200`): Check-worthy assertion lacking verified proof (Data Void).
  - Hovering reveals a sleek floating glass card showing the accredited fact-check citation, source URL, and stance alignment score.

### Wave 2: Interactive GLTR Token Inspector & Statistical Entropy
- **Task 2.1: Token-Level Probability Binning**
  - *Backend*: In `src/synthetic/forensics.py`, calculate conditional log-likelihood and token ranking bins for each token in the text (Top 10, Top 100, Top 1000, Out-of-Vocabulary).
- **Task 2.2: Interactive Token Heatmap UI**
  - *Frontend*: In `#forensics`, render the full analyzed text as color-coded interactive token pills:
    - 🟩 Green: Top-10 most predictable tokens (typical of LLMs).
    - 🟨 Yellow: Top-100 tokens.
    - 🟥 Red: Top-1000 tokens.
    - 🟪 Purple: Rare / Creative / Human tokens.
  - Hovering on any word displays its exact calculated rank $r(w_i)$ and perplexity impact.

### Wave 3: Living Knowledge Graph Temporal Playback & Centrality
- **Task 3.1: Graph Temporal Timestamps & Degree Centrality**
  - *Backend*: Enhance `src/db/sqlite_store.py` to index entity appearance timestamps and calculate in/out-degree centrality.
- **Task 3.2: Chronological Playback Slider ("Time-Lapse")**
  - *Frontend*: Add an interactive time-scrubber beneath `#kg-canvas` ($t_{\text{start}} \to t_{\text{now}}$).
  - Dragging the slider filters visible nodes and edges dynamically, letting examiners watch how claims propagate and connect over time.
  - Node radius scales dynamically with degree centrality.

### Wave 4: Authoring Citation Assistant & Extended Multi-Attack Suite
- **Task 4.1: Pre-Flight AI Citation & Neutrality Suggester**
  - *Backend & Frontend*: In `#preflight`, provide 1-click recommendations for unsupported claims and a **"Neutralize Tone"** button that flags sensationalist clickbait adjectives.
  - *Tamper-Proof Certificate*: When publishing a draft, generate a cryptographic SHA-256 manifest hash displayed as an exportable "Epistemic Provenance Certificate".
- **Task 4.2: Dual-Attack Adversarial Sandbox (TextFooler + DeepWordBug)**
  - *Backend*: Add `DeepWordBug` character typo perturbations (swap, delete, substitute) alongside `TextFooler` synonym substitution.
  - *Frontend*: Render a side-by-side comparison table showing how Naive BERT degrades by $>50\%$ under character typos, while TruthLens maintains $>90\%$ robustness.

---

## 3. Technical Review: How Each Component Will Be Implemented

### Component A: Domain-Adaptive Temporal Decay
- **Algorithm**:
  Instead of a static decay $\exp(-\lambda \Delta t)$, the decay module computes:
  $$\lambda(d) = \lambda_0 \cdot \gamma_{\text{domain}}$$
  Where $\gamma_{\text{domain}} \in \{3.5 \text{ (politics)}, 1.0 \text{ (health)}, 0.1 \text{ (science)}\}$.
  This reflects real-world epistemic stability: a political cabinet statement becomes obsolete within days, while an astronomical observation remains valid for months.

### Component B: Annotated Sentence-Level Reader
- **DOM Architecture**:
  The article text is split using a robust sentence boundary parser. Each sentence $s_i$ is mapped to its corresponding claim $c_i$ in `state.claims`.
  ```html
  <span class="inline-claim highlight-verified" data-claim-idx="0" onmouseenter="showClaimTooltip(event, 0)">
    India successfully launched the Chandrayaan-3 mission.
  </span>
  ```
  A centralized, high-performance absolute-positioned tooltip (`#claim-proof-tooltip`) renders smoothly with zero layout thrashing (`transform: translate3d(...)`).

### Component C: GLTR Token Probability Ranker
- **Mathematical Formulation**:
  Using a statistical n-gram token language model with Good-Turing smoothing, each token $w_i$ is scored against the conditional vocabulary distribution $P(w_i \mid w_{i-2}, w_{i-1})$.
  - Rank 1–10: High probability (Machine-generated boilerplate).
  - Rank 11–100: Moderate probability.
  - Rank 101–1000: Low probability.
  - Rank > 1000: Creative human idiosyncrasy.
  The UI renders tokens inside a flex-wrap container with monospace styling and instant color-coded visual contrast.

### Component D: DeepWordBug Character-Level Attack
- **Perturbation Operations**:
  1. *Swap*: Invert adjacent characters (`"vaccine"` $\to$ `"vaciine"`).
  2. *Replace*: Typo keyboard proximity replacement (`"president"` $\to$ `"presodent"`).
  3. *Delete*: Omit random internal vowel (`"government"` $\to$ `"govrnment"`).
  The simulator quantifies the degradation of standard NLP models when malicious actors intentionally introduce typos to evade basic word-level filters.

---

## 4. Verification Protocol & Done Criteria

| Feature Wave | Falsifiable Done Condition | Verification Method |
|---|---|---|
| **Wave 1** | Inline text reader renders green, red, and yellow highlights with interactive tooltip citations | Playwright browser test asserting `.highlight-verified` and tooltip visibility |
| **Wave 2** | GLTR token heatmap displays 100% of tokens in color-coded bins with hover probability popup | Automated test loading sample text and asserting token count $> 20$ with valid CSS classes |
| **Wave 3** | Time-slider dynamically filters canvas nodes without crashing or throwing console errors | Automated test moving slider value and asserting node count changes |
| **Wave 4** | DeepWordBug introduces typos; citation assistant suggests valid sources | Unit tests in `tests/test_adversarial.py` and Pre-flight UI click test |
| **Deployment** | Git commit pushed to `main`; Render web service deploys `live` with zero 500 errors | HTTP probe asserting `/api/v1/health` and `/api/v1/verify` return 200 OK |

