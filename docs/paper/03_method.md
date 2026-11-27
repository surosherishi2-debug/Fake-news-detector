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

```
[TODO/UNVERIFIED]
- Document exact parameter dimensions, embedding models, and vector retrieval indices selected in Phase 1 and Phase 3.
- Specify whether graph cascade representations will be trained on empirical cascades or maintained as SIMULATED DEMO (Decision pending Phase 5).
```
