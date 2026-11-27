# 6. Discussion

## 6.1 Epistemic Grounding vs. Lexical Overfitting
Our audit of the base repository (`docs/REPO_AUDIT.md`) and prior literature confirms that monolithic text classification models are prone to learning spurious lexical correlations rather than evaluating epistemic veracity. By anchoring verification directly to retrieved primary citations and accredited fact-checks, the model architecture shifts from unconstrained generation to grounded entailment.

## 6.2 The Role of Temporal Obsolescence
Temporal decay prevents historical fact-checks from inappropriately invalidating contemporary developments. The domain-adaptive decay formulation reflects epistemological reality: empirical physical sciences exhibit decades-long stability, whereas political assertions and breaking news evolve rapidly.

## 6.3 Qualitative Error Analysis
A systematic failure mode analysis across 35 concrete misclassifications (`docs/ERROR_ANALYSIS.md`) revealed six distinct failure archetypes:
1. **Numerical & Statistical Distortions (28.6%):** Models frequently over-index on nominal entity tokens while failing to verify arithmetic magnitude, percentage changes, or budget baselines against evidence tables.
2. **Evidence Void / DATA_VOID Boundary (22.9%):** In the absence of corroborating or refuting evidence, uncalibrated models hallucinate certainty or conflate unverified claims with deliberate fabrication.
3. **Temporal Obsolescence / Time Horizon Drift (17.1%):** Claims valid at point-in-time publication were misjudged when evaluated against subsequent statistical updates without temporal decay weighting.
4. **Complex Syntactic Negation & Polarity (14.3%):** Multi-clause sentences featuring double negatives or embedded denials inverted classification polarity in shallow models.
5. **Biomedical & Domain Lexical Drift (11.4%):** Specialized clinical vocabulary tripped generic encoders unable to distinguish nuanced scientific consensus from medical misinformation.
6. **Subtle Sarcasm & Rhetorical Hyperbole (5.7%):** High lexical overlap with legitimate news masked satirical irony.

## 6.4 Engineering Rigor and Enterprise MLOps
The transition from an academic prototype to an industry-grade system requires eliminating hidden assumptions (R1) and unverified metrics (R2). By enforcing a 70.1% automated test coverage ceiling, pinning all 267 environment dependencies in `requirements-lock.txt`, and packaging the complete lifecycle in a single reproducible Docker container, TruthLens-Omni establishes an empirical standard for open, verifiable computational fact-checking.
