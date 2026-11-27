# 3. Method

## 3.1 Overview of Architecture
TruthLens-Omni combines statistical NLP, evidence retrieval, temporal weighting, and neural representation into a tri-modal decision pipeline.

## 3.2 Atomic Claim Decomposition
Given input document $D$, the system segments $D$ into candidate assertions $S = \{s_1, s_2, \dots, s_n\}$ and estimates check-worthiness $c(s_i) \in [0, 1]$. Sentences exceeding threshold $\tau_{\text{claim}}$ are retained for external verification.

## 3.3 Temporal Credibility Decay
Retrieved evidence records $E$ are weighted by their temporal offset relative to claim publication date $t_{\text{claim}}$:
$$w(t) = \exp(-\lambda \cdot \Delta t)$$
where $\Delta t = |t_{\text{claim}} - t_{\text{evidence}}|$ in years, and $\lambda$ is a domain-adaptive decay parameter ($\lambda_{\text{politics}} = 0.35$, $\lambda_{\text{health}} = 0.10$, $\lambda_{\text{science}} = 0.01$).

## 3.4 Context-Enhanced Attention Mechanism (CEAM)
For candidate claim tokens $Q$ and retrieved evidence tokens $K, V$, the temporal-weighted cross-attention is formulated as:
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^\top}{\sqrt{d_k}} \cdot w(t)\right) V$$
Claim representations are subsequently fused with cascade representations via a gated cross-modal unit:
$$z = \sigma(W_g [h_{\text{text}} \,\|\, h_{\text{graph}}] + b_g)$$
$$h_{\text{fused}} = z \odot h_{\text{text}} + (1 - z) \odot h_{\text{graph}}$$

## 3.5 Bipartisan Bridging Matrix Factorization
For community note ratings $r_{ui} \in [-1, 1]$ submitted by user $u$ for note $i$, ratings are decomposed as:
$$\hat{r}_{ui} = \mu + b_u + b_i + \mathbf{p}_u^\top \mathbf{q}_i$$
where $b_i$ represents the bridging helpfulness parameter rewarded when raters with diverse latent ideologies $\mathbf{p}_u$ concur.

## 3.6 Two-Stage Dense Semantic Retrieval & Multi-Factor Re-Ranking
To ground incoming claims against accredited knowledge repositories without web-scraping latency, the system implements a two-stage retrieval pipeline:
1. **Stage 1 (Dense Cosine Similarity):** The claim text $q$ is embedded into a shared 384-dimensional multilingual semantic space using `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`:
   $$S_{\text{dense}}(q, d) = \frac{\mathbf{e}_q \cdot \mathbf{e}_d}{\|\mathbf{e}_q\|_2 \|\mathbf{e}_d\|_2}$$
   where $\mathbf{e}_d$ are pre-computed normalized embeddings of accredited ClaimReview documents in $\mathcal{K}$.
2. **Stage 2 (Multi-Factor Re-ranking):** Top-$k$ candidates ($k=10$) are re-ranked via a composite objective combining dense alignment, token-level lexical overlap ($S_{\text{lex}}$), publisher historical credibility ($W_{\text{auth}}$), and temporal credibility decay ($w(t, d)$):
   $$\text{Score}(q, d) = \begin{cases} (0.70 S_{\text{dense}} + 0.30 S_{\text{lex}}) \cdot (0.80 + 0.20 W_{\text{auth}}) \cdot w(t, d) & \text{if } S_{\text{dense}} \ge 0.20 \\ 0 & \text{otherwise} \end{cases}$$
   Filtering low-density candidates ($S_{\text{dense}} < 0.20$) guarantees that high publisher authority cannot artificially promote semantically irrelevant records.

## 3.7 Calibrated Epistemic Abstention ($DATA\_VOID$ Boundary)
A primary vulnerability of automated misinformation classifiers is closed-world hallucination—assigning binary real/fake labels to ungrounded or novel claims. TruthLens-Omni defines an empirical decision boundary over the maximum retrieved semantic similarity $S_{\max} = \max_{d \in \mathcal{K}} S_{\text{dense}}(q, d)$:
$$\text{Verdict}(q) = \begin{cases} \text{DATA\_VOID} & \text{if } S_{\max} < \tau_{\text{abstain}} = 0.40 \\ \text{Classify}(q, \text{TopEv}(q)) & \text{if } S_{\max} \ge \tau_{\text{abstain}} \end{cases}$$
When $S_{\max} < 0.40$, the system abstains completely from asserting truth or falsehood, outputs confidence 0.0, and flags the claim for provisional human consensus.

## 3.8 Epistemic Nutrition Card & Transparent Saliency Trail
Every evaluated assertion produces an FDA-style 5-dimensional Epistemic Nutrition Card:
1. **Factual Grounding Score:** Percentage of claims backed by verified ClaimReview citations ($[0, 100]$).
2. **Source Transparency Score:** Domain credibility rating derived from accredited press registries.
3. **Organic Diffusion Score:** Inverse coordinated inauthentic behavior (CIB) risk score ($1.0 - \text{CIB}$).
4. **Sensationalism / Clickbait Score:** Saliency penalty from hyperbolic rhetoric, punctuation bursts, and emotional triggers.
5. **Temporal Freshness Score:** Minimum evidence temporal retention weight $w(t) \times 100$.

```
[NOTE ON GRAPH MODULE]
- Graph cascade representations are presently evaluated under Phase 5 governance (Decision pending Phase 5 Gate).
```
