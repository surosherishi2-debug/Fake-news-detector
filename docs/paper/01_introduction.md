# 1. Introduction

## 1.1 Motivation and Problem Statement
The proliferation of deceptive narratives, coordinated inauthentic behavior, and synthetic multimodal misinformation poses severe challenges to democratic deliberation, scientific consensus, and institutional trust. Traditional automated misinformation detection systems rely heavily on monolithic text-only classifiers (such as TF-IDF with linear classifiers or fine-tuned Transformer encoders). While capable of achieving high in-distribution accuracy on benchmark datasets, text-only architectures suffer from critical vulnerabilities:
1. **Factual-Assertion Density:** Deceptive articles frequently interleave accurate factual assertions with isolated, consequential falsehoods. Monolithic sentence-level or document-level classification fails to isolate the exact refuted claims.
2. **Temporal Obsolescence:** Factual truth is temporally conditioned. Scientific and geopolitical events evolve; historical fact-checks cannot be naively projected forward without temporal decay modeling.
3. **Adversarial Brittleness:** Text-only encoders over-index on surface lexical patterns and collapse under adversarial synonym substitutions (e.g. TextFooler).
4. **Data-Void Vulnerability:** Standard classifiers force a closed-world decision, hallucinating confidence on breaking news events where no historical evidence exists.

## 1.2 System Overview: TruthLens-Omni
TruthLens-Omni is engineered as an epistemic intelligence and publishing integrity platform that addresses these failure modes. The architecture decomposes unstructured text into atomic verifiable assertions, retrieves contemporary accredited fact-checks, attenuates historical evidence via an exponential temporal decay function $w(t) = \exp(-\lambda \Delta t)$, evaluates social cascade propagation dynamics, and implements bipartisan consensus modeling.

## 1.3 Contributions and Milestones
- **Comprehensive Base Repository Audit:** In Phase 0, we performed a line-by-line audit of the base implementation (`https://github.com/surosherishi2-debug/Fake-news-detector`), cataloging existing heuristic logic, identifying orphaned deep learning modules, and formally refuting hardcoded benchmark numbers (`docs/REPO_AUDIT.md`, `docs/CLAIMS_AUDIT.md`).
- **Target Milestone (~50%):** A verified, reproducible end-to-end pipeline that takes a user claim or URL, performs factual decomposition, retrieves verified evidence, provides calibrated uncertainty and an epistemic nutrition card, backed by models trained, benchmarked, and logged in `experiments/`.

```
[TODO/UNVERIFIED]
- Incorporate exact empirical figures from Phase 3 experiments once trained.
- State formal hypothesis on adversarial robustness retention once TextAttack benchmarks run.
```
