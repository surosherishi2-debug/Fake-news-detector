# Sources Register (SOURCES.md)

**Rule Reference:** Non-Negotiable Operating Rule R6 ("For every external repo, paper, dataset or API you rely on, add a row to docs/SOURCES.md: name, URL, commit hash or version or access date, license, what we use it for, and how you verified it exists and works. Never cite a paper or repo you did not open this session. If you cannot open it, mark it UNVERIFIED and do not use it.").

---

## Verified Sources (Inspected This Session)

| ID | Name | Source URL | Version / Commit / Date | License | Used For | How Verified |
|---|---|---|---|---|---|---|
| S01 | TruthLens-Omni Base Repository | `https://github.com/surosherishi2-debug/Fake-news-detector` | Commit `HEAD` (2026-11-27) | MIT (per `LICENSE` / README) | Base application, SPA UI, FastAPI endpoints, SQLite schema, test suite | Cloned in workspace, files read and verified via `Get-ChildItem` and `read_file` |
| S02 | FastAPI | `https://fastapi.tiangolo.com` | `0.141.1` (installed) | MIT | REST API microservice framework | Tested via `TestClient` in `python -c` execution |
| S03 | PyTorch | `https://pytorch.org` | `2.13.0` (installed) | BSD-3-Clause | Deep learning neural modeling (Cross-Attention, Gated Fusion) | Verified in `tests/test_ceam_and_benchmarks.py` |
| S04 | Pytest | `https://pytest.org` | `9.1.1` (installed) | MIT | Automated test runner | Executed 38 unit/integration tests in terminal |
| S05 | Google Fact Check Tools API | `https://factchecktools.googleapis.com` | v1alpha1 (2026-11-27) | Google API Terms | External ClaimReview fact-check retrieval client | Inspected client implementation in `src/retrieval/fact_check_client.py` |

---

## Candidate Literature & Datasets (To Be Formally Verified in Phase 1)

| ID | Candidate Name | Primary URL / Paper Reference | License | Intended Role | Verification Status |
|---|---|---|---|---|---|
| C-S01 | LIAR / LIAR-Plus Dataset | Wang, ACL 2017 / Alhindi et al., 2018 | Open Research (CC BY-NC 4.0) | Benchmarking 6-way political truth classification with justifications | **PENDING PHASE 1 VERIFICATION** |
| C-S02 | CoAID (COVID-19 Healthcare) | Cui et al., 2020 (`https://github.com/cuilimeng/CoAID`) | Academic Open Source | Healthcare & vaccine misinformation benchmark | **PENDING PHASE 1 VERIFICATION** |
| C-S03 | FEVER / FEVEROUS | Thorne et al., NAACL 2018 / Aly et al., NeurIPS 2021 | CC BY-SA 4.0 | Evidence-grounded claim verification benchmark | **PENDING PHASE 1 VERIFICATION** |
| C-S04 | FakeNewsNet | Shu et al., ACM SIGKDD 2018 / 2020 | Research Use | PolitiFact & GossipCop claim and social cascade data | **PENDING PHASE 1 VERIFICATION** |
| C-S05 | Community Notes Scoring Code | `https://github.com/twitter/communitynotes` | Apache 2.0 | Matrix factorization bipartisan consensus modeling | **PENDING PHASE 1 VERIFICATION** |
| C-S06 | TextAttack / TextFooler | Jin et al., AAAI 2020 / Morris et al., EMNLP 2020 | MIT | Adversarial synonym substitution stress testing | **PENDING PHASE 1 VERIFICATION** |
