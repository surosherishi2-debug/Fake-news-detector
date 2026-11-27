# Project Backlog (BACKLOG.md)

**Rule Reference:** Non-Negotiable Operating Rule R11 ("NO SCOPE CREEP. Do only what the current phase file lists. Ideas go into docs/BACKLOG.md.").

---

## Deferred Features & Future Enhancements

| Item ID | Proposed Feature / Idea | Origin Phase | Target Phase / Milestone | Notes & Rationale for Deferral |
|---|---|---|---|---|
| B01 | Real-time multimodal audio/video deepfake analysis | Phase 0 | Post-50% Milestone | Current project target (~50% milestone) focuses strictly on textual claim verification, factual retrieval, and epistemic calibration. |
| B02 | Live Twitter/X API firehose ingestion | Phase 0 | Post-50% Milestone | X API requires commercial academic tier keys. Offline propagation cascades or public benchmarks (FakeNewsNet, Twitter15/16) are prioritized. |
| B03 | Chrome Web Store official package deployment | Phase 0 | Phase 7 | Local developer unpacked extension is sufficient for judging and demo. |
| B04 | Kubernetes Helm chart for distributed microservices | Phase 0 | Post-50% Milestone | Docker Compose (`docker compose up`) meets all reproducible packaging criteria for Phase 6. |
| B05 | Direct WhatsApp / Telegram bot verification webhook | Phase 0 | Post-50% Milestone | REST API endpoints `/api/v1/verify` can be wrapped into bots later. |
| B06 | Active learning loop for user feedback corrections | Phase 0 | Post-50% Milestone | Requires persistent human annotation pipeline and moderation queue. |
