# 7. Limitations

## 7.1 Scope of Current Work
1. **Reliance on External Fact-Check Availability:** When evaluating novel or breaking claims that fall into an empirical data void (zero recorded ClaimReview entries), the system must abstain with a `DATA_VOID` / `UNCERTAIN` verdict. It cannot synthesize autonomous ground truth without evidence.
2. **Computational Constraints:** Real-time transformer cross-attention across multiple retrieved candidate documents introduces latency constraints relative to simple linear baselines.
3. **Multilingual Tokenizer Representation:** While multilingual tokenizers (e.g. XLM-R) support Indic scripts, morphologically rich languages like Marathi may require specialized subword vocabulary adaptation.
4. **Graph Cascades in Real Time:** Social propagation graphs are often incomplete or unavailable at the time a claim is first published, necessitating decoupled or simulated cascade analysis in offline testing.

```
[TODO/UNVERIFIED]
- Update limitations section following empirical error analysis and latency benchmarks in Phase 3 and Phase 4.
```
