# 7. Limitations

## 7.1 Scope of Current Work
1. **Reliance on External Fact-Check Availability:** When evaluating novel or breaking claims that fall into an empirical data void (zero recorded ClaimReview entries), the system must abstain with a `DATA_VOID` / `UNCERTAIN` verdict. It cannot synthesize autonomous ground truth without evidence.
2. **Computational Constraints:** Real-time transformer cross-attention across multiple retrieved candidate documents introduces latency constraints relative to simple linear baselines.
3. **Multilingual Tokenizer Representation:** While multilingual tokenizers (e.g. XLM-R) support Indic scripts, morphologically rich languages like Marathi may require specialized subword vocabulary adaptation.
4. **Graph Cascades in Real Time:** Social propagation graphs are often incomplete or unavailable at the time a claim is first published, necessitating decoupled or simulated cascade analysis in offline testing.

## 7.2 Empirical Boundary Conditions
1. **CPU Batching Constraints:** Training without GPU acceleration necessitated restricting transformer sequence lengths to 128 tokens and batch sizes to 32. While sufficient for claims and abstract summaries, processing long-form investigative articles requires document chunking or GPU acceleration.
2. **Indic Regional Benchmark Scale:** Although the multilingual encoder demonstrated 100% accuracy on the curated 10-sample Indic benchmark, broader regional deployment requires expanding dialectal coverage across low-resource Indic languages to $\ge 5,000$ verified debunks.
3. **Simulated Social Cascades:** In the absence of live API access to social network graph topologies at publication time, cascade topology analysis relies on heuristic graph feature simulations (`HeteroGraphEncoder` [SIMULATED DEMO]), pending ingestion of real temporal diffusion trees (e.g. PHEME/Twitter15).
4. **Third-Party Rate Limits:** Live claim verification depends on the Google Fact Check Tools API and external publisher availability, subject to network latency and upstream quota constraints.
