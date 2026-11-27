# Open Questions Register (OPEN_QUESTIONS.md)

**Rule Reference:** Non-Negotiable Operating Rule R1 ("If a fact, path, API behavior, dataset property, license, version, or requirement is not visible in the workspace, read from an official source this session, or produced by a command you ran, you may not state it. Record it in docs/OPEN_QUESTIONS.md and either verify it or STOP that task and ask me.").

---

| ID | Question / Unresolved Item | Raised By / Phase | Assigned To | Blocking? | Status | Current Resolution / Next Action |
|---|---|---|---|---|---|---|
| Q01 | Does `PuneFakeNews-2024` exist as an external dataset, or was it created as an in-repo synthetic mock? | Phase 0 | User / Literature Search | No (Non-blocking for Phase 0/1) | **OPEN** | In Phase 1 research, search for published references. If nonexistent, replace with genuine multilingual/Indic benchmark (e.g. IndicData, FakeNewsNet, or curated Hindi/Marathi fact-checks from IFCN). |
| Q02 | Do pre-trained weights exist for `CEAMTruthLensModel` from an earlier training run, or must we train from scratch? | Phase 0 | User | No (Non-blocking for Phase 0/1) | **OPEN** | Assume training from scratch in Phase 3 unless user provides a weights checkpoint. |
| Q03 | Was `EDI.researchpaper.pdf` or an IEEE TNN 2024 paper actually published, or is it a project proposal draft? | Phase 0 | User | No | **OPEN** | Treat all paper references as hypotheses. In Phase 1, search academic literature for official DOIs. |
| Q04 | What local/cloud hardware configuration should be prioritized for training in Phase 3? | Phase 0 | User | No | **OPEN** | Python 3.12 with PyTorch 2.13 CPU/CUDA detected. Will verify local CUDA availability before Phase 3 model ladder. |
| Q05 | Should the Chrome extension be bundled in the Phase 6 Docker / reproduction package or kept standalone? | Phase 0 | Architect | No | **OPEN** | Keep standalone in `chrome-extension/` with instructions in README. |
