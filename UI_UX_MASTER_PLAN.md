# TruthLens-Omni: UI/UX Master Plan & Frontend Architecture
## Neo-FinTech Design System, 5 Core Operational Pages, Landing, Auth & Profile

**Specification Document:** `UI_UX_MASTER_PLAN.md`  
**Design Reference:** Soft Modern Neo-FinTech Dashboard Architecture  
**Target Maturity:** Jump from ~10% Backend Core to ~45% Full-Stack Working System

---

## 1. Design System & Visual Identity Translation

The visual architecture directly operationalizes the design aesthetics of the reference interface: high contrast between light metric cards on top and an elevated, high-density dark split-card container on the bottom.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   TRUTHLENS-OMNI COLOR ARCHITECTURE                                     │
├─────────────────────────┬─────────────────────────┬─────────────────────────────────────────────────────┤
│ Token                   │ Hex Value               │ Usage in UI                                         │
├─────────────────────────┼─────────────────────────┼─────────────────────────────────────────────────────┤
│ Surface-Canvas          │ #F4F5FA / #F8F9FD       │ Light outer background with subtle grey tint        │
│ Surface-Elevated        │ #FFFFFF                 │ Top metric cards, active filters, dropdowns         │
│ Surface-Dark-Container  │ #0F131D / #121622       │ High-contrast master-detail split container         │
│ Surface-Dark-Elevated   │ #3D3594 / #4E43D8       │ Deep violet/indigo inner active card container      │
│ Primary-Accent          │ #5E4BF5 / #6366F1       │ Active pill tabs, primary buttons, focus rings      │
│ Text-Primary-Light      │ #111827                 │ Dark headings on light surfaces                     │
│ Text-Muted-Light        │ #6B7280                 │ Subtitles, timestamps, secondary metrics            │
│ Text-Primary-Dark       │ #FFFFFF                 │ High-contrast text on dark containers               │
│ Text-Muted-Dark         │ #A5B4FC / #9CA3AF       │ Subtitles on dark containers                        │
│ Status-Verified (Green) │ #10B981                 │ 🟢 Verified factual claims, high trust              │
│ Status-Refuted (Red)    │ #EF4444                 │ 🔴 Refuted / Debunked claims, botnet alert          │
│ Status-DataVoid (Amber) │ #F59E0B                 │ 🟡 Data-void, unverified, breaking news             │
│ Status-Satire (Violet)  │ #8B5CF6                 │ 🟣 Parody / Satirical news marker                   │
└─────────────────────────┴─────────────────────────┴─────────────────────────────────────────────────────┘
```

### 8-Point Spatial Grid & Component Hierarchy
- **Canvas Rhythm:** All paddings, margins, and gaps strictly adhere to: `4px`, `8px`, `12px`, `16px`, `24px`, `32px`, `48px`.
- **Corner Radii:** Outer container `rounded-3xl` (24px), inner cards `rounded-2xl` (16px), pills and badges `rounded-full` (9999px).
- **Typography:** Sans-serif (`Plus Jakarta Sans` or `Inter`), with numbers set to `tabular-nums` for alignment.

---

## 2. Complete Page Architecture & Navigation Map

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   TRUTHLENS-OMNI SITEMAP & ROUTING                                      │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│   Public Tier:                                                                                         │
│   ├── ( / )                     ──► Modern Showcase Landing Page (Hero, Live Input, Pitch Teaser)      │
│   └── ( /auth )                 ──► Auth Module (Sign In, Register, Role Selector, API Keys)           │
│                                                                                                        │
│   Authenticated Application Tier:                                                                      │
│   ├── [ Top Navigation Pill Bar: Search, Notifications, Language Toggle (En/Hi), Profile Avatar ]     │
│   │                                                                                                    │
│   ├── ( /app/verify )           ──► PAGE 1: Deep Verification & Live Claim Studio                      │
│   ├── ( /app/cascades )         ──► PAGE 2: Social Cascades & CIB Botnet Radar                         │
│   ├── ( /app/consensus )        ──► PAGE 3: Community Bridging Consensus Hub                          │
│   ├── ( /app/multimodal )       ──► PAGE 4: Multimodal Cheapfake & Media Lab                           │
│   ├── ( /app/trends )           ──► PAGE 5: Global Trends & Indic Intelligence                         │
│   └── ( /app/profile )          ──► Profile & Trust Center (Reputation, Note History, API Keys)        │
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications for All Pages

### 3.1 Public Landing Page (`/`)
* **Hero Section:** High-impact pitch: *"The World's First Tri-Modal Misinformation Intelligence Platform."*
* **Interactive Live Analyzer Widget:** Prominent search/URL input field allowing immediate testing on sample claims or live links without initial sign-in.
* **Academic Pedigree Section:** Highlights the IEEE 2024 paper, MIT-WPU & IIT Bombay research lineage, and the $78B global economic impact problem statement.
* **Live Global Misinformation Ticker:** Displays real-time data-void alerts and recently refuted claims.
* **CTA Button:** *"Launch Intelligence Dashboard"* directing to Auth / App.

---

### 3.2 Authentication & Role Selection Module (`/auth`)
* **Sign-In & Onboarding:**
  - Standard OAuth (Google / GitHub) + Email Magic Link.
  - **Role Selection:**
    1. *Digital Citizen / Reader:* Read-only verified nutrition cards and Chrome extension sync.
    2. *Verified Fact-Checker (IFCN):* Access to claim decomposition, evidence submission, and editorial notes.
    3. *Trust & Safety Officer:* High-throughput API keys, cascade graph analytics, and CIB botnet cluster alerts.
    4. *Academic Researcher / Evaluator:* Direct access to raw dataset splits, model weights, and benchmark evaluations.
* **API Key Provisioning:** Generates JWT tokens and REST API keys for programmatic consumption.

---

### 3.3 Page 1: Deep Verification & Live Claim Studio (`/app/verify`)
*Features Integrated:* **F10** (URL Scraper), **F2** (Sentence Claim Highlighter), **F6** (Satire Filter), **F1** (Contextual Nutrition Card), **F9** (Causal XAI Provenance).

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  Top Bar: [ TruthLens ]  ( Overview ) ( Estimates ) (• Verify ) ( Cascades ) ( Consensus ) ... [Avatar]│
├──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  Top Metrics Row (White Cards on #F4F5FA Canvas):                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐              │
│  │ Factual Grounding│  │ Evidence Freshness│ │ Cascade Risk     │  │ Overall Verdict  │              │
│  │ 84.2%            │  │ w(t) = 0.94      │  │ Low (0.18)       │  │ REAL / VERIFIED  │              │
│  │ +3.2% vs baseline│  │ 2 days old       │  │ Normal diffusion │  │ High Confidence  │              │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘              │
├──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  Bottom Split Container (Dark High-Contrast Card #0F131D):                                           │
│  ┌──────────────────────────────────────────────┬──────────────────────────────────────────────────┐ │
│  │ Left Panel: Atomic Claim Sentence Stream     │ Right Panel: Active Claim Deep-Dive & Evidence   │ │
│  │                                              │ (Elevated Soft Purple Container #3D3594)         │ │
│  │ • 🟢 [VERIFIED] Sentence 1: "ISRO confirmed..."│ Claim #1: "ISRO confirmed lunar sulfur detected" │ │
│  │ • 🔴 [REFUTED] Sentence 2: "Found alien..."  │ Stance: REFUTED by Accredited Fact-Checker       │ │
│  │ • 🟡 [DATA_VOID] Sentence 3: "Private talks" │                                                  │ │
│  │                                              │ Primary Source: PIB Fact-Check Unit (Doc #992)   │ │
│  │ [Filter: All (3) | Verified (1) | Fake (1)]  │ URL: https://pib.gov.in/factcheck/isro-moon      │ │
│  │                                              │                                                  │ │
│  │                                              │ [ Nutrition Card Radar: 5 Normalized Scores ]    │ │
│  │                                              │ Grounding: 88 | Trust: 94 | Organic: 90          │ │
│  │                                              │                                                  │ │
│  │                                              │ Action: [ View Source ] [ Copy Context Note ]    │ │
│  └──────────────────────────────────────────────┴──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.4 Page 2: Social Cascades & CIB Botnet Radar (`/app/cascades`)
*Features Integrated:* **F3** (Coordinated Inauthentic Behavior Burst Detector), 3-Layer Heterogeneous Graph Transformer (HGT), Live Bluesky Firehose Ingestion.
* **Top Metric Cards:**
  1. *Active Cascade Graphs:* Count of monitored viral threads (e.g. 14,280).
  2. *CIB Botnet Anomaly Spikes:* Count of active astroturfing campaigns flagged in the last 24h.
  3. *Synchronized Burst Rate:* Median retweeting interval across active clusters (e.g. 12 seconds).
  4. *Verified User Diffusion Ratio:* Percentage of organic verified account participation.
* **Bottom Dark Split-View Container:**
  - **Left Side:** Real-time cascade feed sorted by CIB risk score with account count badges.
  - **Right Side:** Interactive **WebGL 2D/3D Network Graph Explorer** (Sigma.js). Renders Article, User, and Publisher nodes. Tightly clustered red nodes indicate botnet coordination; spread green nodes show organic cross-community diffusion.

---

### 3.5 Page 3: Community Bridging Consensus Hub (`/app/consensus`)
*Features Integrated:* **F4** (Decentralized Matrix Factorization Bridging Consensus Engine from X Community Notes).
* **Top Metric Cards:**
  1. *Notes in Review:* Active crowd fact-check proposals.
  2. *Bipartisan Consensus Rate:* Percentage of notes achieving cross-ideological agreement ($b_i \ge 0.35$).
  3. *Rater Polarization Spread:* Active rater ideological diversity variance.
  4. *Fast-Track AI Seeded Notes:* Notes auto-drafted by TruthLens awaiting human ratification.
* **Bottom Dark Split-View Container:**
  - **Left Side:** Filterable list of candidate context notes (`Needs More Ratings`, `Helpful`, `Not Helpful`).
  - **Right Side:** Matrix Factorization latent factor visualizer: displays the rater ideological distribution curve ($\mathbf{p}_u$), the note helpfulness intercept ($b_i$), and an interactive rating submission box.

---

### 3.6 Page 4: Multimodal Cheapfake & Media Lab (`/app/multimodal`)
*Features Integrated:* **F8** (Google SigLIP ViT-SO400M Cross-Modal Contradiction Validator), OCR & Reverse-Image Ingestion.
* **Top Metric Cards:**
  1. *Modality Entailment Score:* Text-image consistency percentage.
  2. *Oldest Visual Origin Year:* Oldest archival match found via reverse visual search.
  3. *Meme OCR Extraction Accuracy:* Text confidence extracted from graphic infographics.
  4. *Visual Manipulation Risk:* Deepfake / cheapfake artifact confidence.
* **Bottom Dark Split-View Container:**
  - **Left Side:** Visual dropzone displaying the uploaded meme or image with OCR bounding box overlays.
  - **Right Side:** Cross-Modal Contradiction Diagnostic: compares caption assertion against archival visual history, flagging temporal and geographical mismatches.

---

### 3.7 Page 5: Global Trends & Indic Intelligence (`/app/trends`)
*Features Integrated:* **F5** (Dynamic Breaking News Data-Void RAG), **F7** (Indic Multilingual Engine - IndicBERT/MuRIL), NewsGuard Domain Leaderboard.
* **Top Metric Cards:**
  1. *Monitored Indian Languages:* English, Hindi, Marathi, Bengali, Tamil, Telugu.
  2. *Breaking Data-Voids:* Unverified breaking news topics with zero existing fact-checks.
  3. *Cross-Lingual Hindi Accuracy:* Tracking performance against the `PuneFakeNews-2024` benchmark.
  4. *Tracked Publisher Domains:* Active domain trust scores (0-100).
* **Bottom Dark Split-View Container:**
  - **Left Side:** Real-time breaking news ticker streaming unverified claims and data voids.
  - **Right Side:** Regional Indian heatmap showing misinformation breakout clusters, and a searchable NewsGuard-style domain reputation directory.

---

### 3.8 Profile & Trust Center (`/app/profile`)
* **User Credibility Tier:** Gamified trust level based on accurate Community Note ratings and verified submissions.
* **Contributed Notes & Voting History:** Personal ledger of rated notes and consensus accuracy.
* **API Key & Usage Quota Management:** Rate limits, webhook callbacks, and usage graphs.
* **System Language & Localization Settings:** Toggle default UI and verification language between English, Hindi (हिंदी), and Hinglish.

---

## 4. Implementation Strategy: Pushing from ~10% to ~45%

To move rapidly to a 45% completion milestone for your advisor presentation, we execute in three sequential sprints:

```
Sprint 1: Interactive Full-Stack Engine & Demo GUI (Immediate)
├── Launch Streamlit / Next.js interactive frontend connected to FastAPI
├── Implement Page 1 (Verification Studio) & Page 3 (Community Notes Consensus)
└── Wire the Contextual Nutrition Card and Sentence Highlighting inline

Sprint 2: Media & Cascade Explorer
├── Connect Page 2 (Cascade Graph Visualizer with Sigma.js)
└── Connect Page 4 (Multimodal image dropzone with SigLIP)

Sprint 3: Global Intel, Auth & Profile
├── Connect Page 5 (Trends & Indic RAG)
└── Wire Authentication, Role Switcher, and Profile Page
```
