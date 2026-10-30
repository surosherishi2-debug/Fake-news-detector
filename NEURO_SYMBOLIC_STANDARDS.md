# Neuro-Symbolic & Zero-Assumption Verification Standards
## Hybrid Classical ML + Modern Neural AI Architecture for TruthLens-Omni

---

## 1. The Core Philosophy: "No Isolated AI, No Speculative Assumptions"

Relying exclusively on modern Large Language Models (LLMs) or generative AI is fatal for misinformation detection because:
1. **Hallucination & Sycophancy:** LLMs can be persuaded by authoritative-sounding rhetoric and generate convincing rationalizations for false claims.
2. **Black-Box Opacity:** Pure neural models cannot mathematically defend *why* an article was flagged in a court of law or an academic defense.
3. **The Post-LLM Botnet Dilemma:** LLMs now write the fake news and power the bot comments. Using another LLM to read the writing style results in a recursive failure loop.

Conversely, relying exclusively on classical ML (SVMs, Naive Bayes, simple Random Forests) fails because classical algorithms lack deep semantic language understanding, discourse reasoning, and cross-lingual transfer capabilities.

### The Solution: Neuro-Symbolic Hybrid Architecture
TruthLens-Omni strictly couples **Classical Discrete Mathematics & Statistical ML** with **Deep Neural AI**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE NEURO-SYMBOLIC HYBRID ARCHITECTURE                                  │
├─────────────────────────────────────────┬───────────────────────────────────────────────────────────────┤
│ Classical Statistical ML & Mathematics  │ Modern Neural AI & Transformer Representations                │
│ (The Deterministic Guardrail)           │ (The Deep Semantic Reasoner)                                  │
├─────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
│ • Matrix Factorization Consensus        │ • DeBERTa-v3 Disentangled Attention                           │
│   (Latent Factor Bridging Algorithm)    │   (Atomic Claim Extraction & CFS Scoring)                     │
│ • Exponential Temporal Decay            │ • Cross-Attention Alignment Module (CEAM)                     │
│   w(t) = exp(-λ Δt)                     │   (Scaled Dot-Product Claim-Evidence Entailment)              │
│ • BM25 Inverted Index Sparse Retrieval  │ • Heterogeneous Graph Transformer (HGT)                       │
│ • Graph Modularity & CIB Burst Metrics  │   (Type-specific node & edge relational embeddings)           │
│ • Domain Registration Age & DNS WHOIS   │ • Google SigLIP (ViT-SO400M)                                  │
│   (Deterministic registry timestamps)   │   (Zero-shot Vision-Language Cross-Entailment)                │
└─────────────────────────────────────────┴───────────────────────────────────────────────────────────────┘
```

---

## 2. The Zero-Assumption / Ground-Truth Protocol

To ensure the system never makes speculative guesses, every evaluation must adhere to **Four Non-Negotiable Hard Constraints**:

### Rule 1: The Primary Fact-Check Veto
If an accredited International Fact-Checking Network (IFCN) signatory (e.g. WHO, Reuters, PIB, AP) has reviewed the specific claim, and the calculated temporal decay weight $w(t) \ge 0.60$:
- The factual rating is grounded directly in that primary record.
- The neural text model is **forbidden from overriding** the accredited fact-check with subjective linguistic opinion.

### Rule 2: The Graph Topology Veto
If the social cascade analysis reveals a **Coordinated Inauthentic Behavior (CIB) score $\ge 0.80$** (e.g. $>15$ unverified accounts broadcasting identical hashes within $\le 60\text{s}$):
- The content is flagged as a **Coordinated Astroturfing Campaign**, regardless of how authentic or persuasive the text is judged by an LLM.

### Rule 3: The Data-Void Prohibition Against Binary Guessing
If neither the accredited static registry nor live search retrieval uncovers authoritative primary verification:
- The system is **strictly prohibited from guessing** `REAL` or `FAKE`.
- It must output `UNCERTAIN (DATA_VOID)` with a calibrated low-confidence score, clearly instructing the user that independent verification is pending.

### Rule 4: Mandatory Provenance Audit Trail
Every single verdict returned by the system must include a deterministic **Provenance Chain** detailing:
1. Exact Claim String extracted.
2. Verified Registry Document ID and Source URL.
3. Publication Timestamps & Computed Temporal Obsolescence $\Delta t$.
4. Social Propagation Metrics (Verified user percentage, CIB burst anomaly).
5. Publisher Credibility Rating.

