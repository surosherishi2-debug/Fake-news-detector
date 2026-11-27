# 2. Related Work

## 2.1 Fact-Checking and Claim Decomposition
Automated fact-checking typically proceeds through claim detection, evidence retrieval, and claim verification. Pioneering systems such as ClaimBuster (Hassan et al., 2017) formulated check-worthiness scoring as a supervised sentence classification task. Recent research has focused on granular claim decomposition, isolating atomic propositions from compound sentences to enable fine-grained evidence alignment.

## 2.2 Temporal Dynamics in Misinformation
Information credibility is inherently time-sensitive. Temporal decay modeling ensures that stale debunks do not invalidate subsequent legitimate developments, while historical consensus in empirical domains (e.g., physical sciences) is preserved over extended half-lives compared to highly volatile political cycles.

## 2.3 Adversarial Vulnerability and Robustness
Adversarial attacks on NLP models, such as TextFooler (Jin et al., 2020) and DeepWordBug (Gao et al., 2018), expose the reliance of neural transformers on superficial token correlations. Grounding predictions on external accredited evidence rather than purely internal token weights provides an architectural defense against adversarial token permutations.

## 2.4 Decentralized Consensus and Social Cascades
In addition to centralized fact-checkers, decentralized bridging consensus algorithms—most prominently X/Twitter Community Notes—utilize low-rank matrix factorization to surface notes that bridge opposing ideological perspectives, mitigating partisan polarization.

```
[TODO/UNVERIFIED]
- Complete systematic survey of 2024-2026 misinformation literature in Phase 1 (Task 1.1 - 1.3).
- Integrate comparative analysis of FEVER, FEVEROUS, LIAR-Plus, and CoAID.
- Formalize the 3-5 specific architectural techniques adopted for the Phase 3 model ladder.
```
