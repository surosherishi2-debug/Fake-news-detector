/**
 * TruthLens-Omni Full-Spectrum Epistemic Platform Controller.
 * Manages Daily Info Feed, Pre-Flight Self-News Studio, Synthetic Forensics,
 * Living Knowledge Graph, Deep Verify, and Matrix Factorization Consensus.
 */

document.addEventListener('DOMContentLoaded', () => {
  const state = {
    activeTab: 'feed',
    currentRole: 'journalist',
    claims: [],
    selectedClaimIndex: 0,
    latestResult: null,
    graphVisualizer: null,
  };

  const tabButtons = document.querySelectorAll('.nav-tab-btn');
  const pageSections = document.querySelectorAll('.page-view');
  const roleBadge = document.getElementById('user-role-badge');
  const authModal = document.getElementById('auth-modal');

  // Navigation Routing
  function initRouting() {
    const hash = window.location.hash.replace('#', '') || 'feed';
    switchTab(hash);

    window.addEventListener('hashchange', () => {
      const target = window.location.hash.replace('#', '') || 'feed';
      switchTab(target);
    });
  }

  function switchTab(tabName) {
    const validTabs = ['feed', 'preflight', 'forensics', 'verify', 'cascades', 'consensus', 'graph', 'multimodal', 'profile'];
    if (!validTabs.includes(tabName)) tabName = 'feed';

    state.activeTab = tabName;
    window.location.hash = tabName;

    // Update Top Pill Bar
    tabButtons.forEach((btn) => {
      const target = btn.getAttribute('data-tab');
      if (target === tabName) {
        btn.classList.add('bg-[#5E4BF5]', 'text-white', 'shadow-sm');
        btn.classList.remove('text-slate-300', 'hover:text-white');
      } else {
        btn.classList.remove('bg-[#5E4BF5]', 'text-white', 'shadow-sm');
        btn.classList.add('text-slate-300', 'hover:text-white');
      }
    });

    // Update Page Views
    pageSections.forEach((section) => {
      if (section.id === `page-${tabName}`) {
        section.classList.remove('hidden');
      } else {
        section.classList.add('hidden');
      }
    });

    // Page-specific trigger actions
    if (tabName === 'feed') loadDailyFeed();
    if (tabName === 'graph') loadLivingKnowledgeGraph();
    if (tabName === 'cascades' && !state.graphVisualizer) setTimeout(() => initCascadePage(), 100);
  }

  tabButtons.forEach((btn) => {
    btn.addEventListener('click', () => switchTab(btn.getAttribute('data-tab')));
  });

  // ==========================================
  // TAB 1: DAILY EPISTEMIC FEED ("Daily Info")
  // ==========================================
  async function loadDailyFeed() {
    const container = document.getElementById('feed-articles-container');
    if (!container) return;

    container.innerHTML = '<div class="p-8 text-center text-slate-400">Loading verified epistemic daily feed...</div>';

    const category = document.getElementById('feed-filter-category')?.value || 'All';
    const status = document.getElementById('feed-filter-status')?.value || 'All';

    try {
      const params = new URLSearchParams({ category, status, limit: '20' });
      const resp = await fetch(`/api/v1/feed?${params.toString()}`);
      const data = await resp.json();

      if (!data.articles || data.articles.length === 0) {
        container.innerHTML = '<div class="p-8 text-center text-slate-400">No stories match active filters.</div>';
        return;
      }

      container.innerHTML = data.articles.map(art => {
        let statusBadge = 'bg-emerald-500/15 text-emerald-700 border-emerald-200';
        let statusIcon = '🟢 VERIFIED REAL';
        if (art.status === 'FAKE') {
          statusBadge = 'bg-rose-500/15 text-rose-700 border-rose-200';
          statusIcon = '🔴 DEBUNKED FAKE';
        } else if (art.status === 'SATIRE') {
          statusBadge = 'bg-purple-500/15 text-purple-700 border-purple-200';
          statusIcon = '🟣 SATIRE PARODY';
        } else if (art.status === 'SYNTHETIC') {
          statusBadge = 'bg-cyan-500/15 text-cyan-700 border-cyan-200';
          statusIcon = '🤖 AI SYNTHETIC';
        } else if (art.status === 'DATA_VOID') {
          statusBadge = 'bg-amber-500/15 text-amber-700 border-amber-200';
          statusIcon = '🟡 BREAKING VOID';
        }

        return `
          <div class="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:border-indigo-300 transition space-y-3">
            <div class="flex items-center justify-between text-xs">
              <span class="px-2.5 py-0.5 rounded-full font-semibold border ${statusBadge}">${statusIcon}</span>
              <span class="text-slate-400">${art.category} • ${art.publisher}</span>
            </div>
            <h3 class="text-base font-bold text-slate-900 leading-snug">${art.title}</h3>
            <p class="text-xs text-slate-600 line-clamp-2 leading-relaxed">${art.content}</p>
            <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <div class="flex items-center gap-3 text-slate-500">
                <span>Integrity: <b class="text-slate-800">${art.truth_score}%</b></span>
                <span>Cascade Risk: <b class="text-slate-800">${(art.cib_risk * 100).toFixed(0)}%</b></span>
              </div>
              <button onclick="inspectFeedArticle('${art.id}', '${encodeURIComponent(art.title)}', '${encodeURIComponent(art.content)}', '${art.domain}')" class="px-3 py-1.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-[#5E4BF5] font-semibold text-xs transition">
                Deep Audit →
              </button>
            </div>
          </div>
        `;
      }).join('');
    } catch (err) {
      container.innerHTML = `<div class="p-8 text-center text-rose-500">Failed to load feed: ${err.message}</div>`;
    }
  }

  window.inspectFeedArticle = function(id, titleEnc, contentEnc, domain) {
    const title = decodeURIComponent(titleEnc);
    const content = decodeURIComponent(contentEnc);
    switchTab('verify');
    document.getElementById('input-text').value = `${title}. ${content}`;
    document.getElementById('input-publisher').value = domain;
    executeVerification();
  };

  const feedFilterCategory = document.getElementById('feed-filter-category');
  const feedFilterStatus = document.getElementById('feed-filter-status');
  if (feedFilterCategory) feedFilterCategory.addEventListener('change', loadDailyFeed);
  if (feedFilterStatus) feedFilterStatus.addEventListener('change', loadDailyFeed);

  // ==========================================
  // TAB 2: PRE-FLIGHT STUDIO ("Audit My Story / Self-News")
  // ==========================================
  const preflightBtn = document.getElementById('btn-run-preflight');
  const preflightDraftInput = document.getElementById('preflight-draft-text');

  if (preflightBtn && preflightDraftInput) {
    preflightBtn.addEventListener('click', async () => {
      const draft_text = preflightDraftInput.value.trim();
      if (!draft_text) return alert('Please enter or draft your story to audit.');

      preflightBtn.innerText = 'Auditing Story Draft...';
      preflightBtn.disabled = true;

      try {
        const resp = await fetch('/api/v1/preflight/audit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ draft_text }),
        });
        const report = await resp.json();
        renderPreflightReport(report);
      } catch (err) {
        alert('Pre-flight audit failed: ' + err.message);
      } finally {
        preflightBtn.innerText = 'Audit My Story Before Publishing';
        preflightBtn.disabled = false;
      }
    });
  }

  window.loadPreflightSample = function() {
    preflightDraftInput.value = (
      "Scientists at ISRO confirmed water ice near the lunar south pole yesterday. " +
      "However, viral internet posts claim COVID-19 vaccines contain secret biometric microchips for surveillance. " +
      "Shocking secret reports suggest local banks are closing without warning!"
    );
  };

  function renderPreflightReport(report) {
    const scoreBox = document.getElementById('preflight-score');
    const assertionsBox = document.getElementById('preflight-assertions-list');
    const recsBox = document.getElementById('preflight-recs-list');

    scoreBox.innerText = `${report.audit_readiness_score}%`;
    scoreBox.className = 'text-3xl font-extrabold tabular ' + (
      report.audit_readiness_score >= 80 ? 'text-emerald-600' : (report.audit_readiness_score >= 50 ? 'text-amber-500' : 'text-rose-600')
    );

    recsBox.innerHTML = report.recommendations.map(r => `
      <li class="flex items-start gap-2 text-xs text-slate-700 font-medium">
        <span class="text-[#5E4BF5] font-bold">›</span>
        <span>${r}</span>
      </li>
    `).join('');

    assertionsBox.innerHTML = report.assertions.map(a => {
      let riskBadge = 'bg-emerald-50 text-emerald-700 border-emerald-200';
      if (a.risk_level === 'HIGH') riskBadge = 'bg-rose-50 text-rose-700 border-rose-200';
      else if (a.risk_level === 'MEDIUM') riskBadge = 'bg-amber-50 text-amber-700 border-amber-200';

      return `
        <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="font-bold text-slate-800">Assertion #${a.sentence_index + 1}</span>
            <span class="px-2 py-0.5 rounded font-semibold border ${riskBadge}">${a.risk_level} RISK</span>
          </div>
          <p class="text-slate-700 italic font-medium">"${a.text}"</p>
          <p class="text-[11px] text-slate-500 font-medium"><b>Action:</b> ${a.suggested_action}</p>
          ${a.recommended_citations.length > 0 ? `
            <div class="text-[11px] text-indigo-700 bg-indigo-50/60 p-2 rounded-lg mt-1">
              <b>Recommended Citations:</b> ${a.recommended_citations.join(' | ')}
            </div>
          ` : ''}
        </div>
      `;
    }).join('');
  }

  // ==========================================
  // TAB 3: SYNTHETIC MEDIA & AI HALLUCINATIONS ("The Real Fake")
  // ==========================================
  const forensicsBtn = document.getElementById('btn-run-forensics');
  const forensicsTextInput = document.getElementById('forensics-text');

  if (forensicsBtn && forensicsTextInput) {
    forensicsBtn.addEventListener('click', async () => {
      const text = forensicsTextInput.value.trim();
      if (!text) return alert('Please enter text to analyze.');

      forensicsBtn.innerText = 'Calculating Entropy & Burstiness...';
      forensicsBtn.disabled = true;

      try {
        const resp = await fetch('/api/v1/forensics/synthetic', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text }),
        });
        const rep = await resp.json();
        renderForensicsReport(rep);
      } catch (err) {
        alert('Forensic analysis failed: ' + err.message);
      } finally {
        forensicsBtn.innerText = 'Run Statistical AI Forensics';
        forensicsBtn.disabled = false;
      }
    });
  }

  window.loadForensicsSample = function(type) {
    if (type === 'ai') {
      forensicsTextInput.value = (
        "In today's digital age, it is crucial to note that quantum computing plays a pivotal role in modern society. " +
        "Furthermore, navigating the complexities of artificial intelligence stands as a testament to human innovation. " +
        "Moreover, it is important to remember that ethical considerations serve as a beacon of hope for future generations. " +
        "In conclusion, we must delve into the tapestry of digital transformation with utmost responsibility."
      );
    } else {
      forensicsTextInput.value = (
        "Stop and check the official ledger. At 4:15 PM on Friday, the council voted 7-2 against the municipal land sale. " +
        "I was standing right in the second row when the mayor walked out. It wasn't expected at all. " +
        "Why would they reverse their stance after three months of public hearings?"
      );
    }
  };

  function renderForensicsReport(rep) {
    document.getElementById('forensics-ai-prob').innerText = `${(rep.ai_generated_probability * 100).toFixed(1)}%`;
    document.getElementById('forensics-burstiness').innerText = rep.burstiness_score;
    document.getElementById('forensics-ttr').innerText = rep.lexical_diversity;
    document.getElementById('forensics-classification').innerText = rep.classification;
    document.getElementById('forensics-explanation').innerText = rep.verdict_explanation;

    const phrasesBox = document.getElementById('forensics-detected-phrases');
    if (rep.detected_phrases.length > 0) {
      phrasesBox.innerHTML = rep.detected_phrases.map(p => `
        <span class="px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 text-xs font-mono font-medium">${p}</span>
      `).join(' ');
    } else {
      phrasesBox.innerHTML = '<span class="text-xs text-slate-400">Zero typical generative LLM transition clichés found.</span>';
    }
  }

  // ==========================================
  // TAB 4: LIVING KNOWLEDGE GRAPH ("The Graph")
  // ==========================================
  async function loadLivingKnowledgeGraph() {
    const canvas = document.getElementById('kg-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = 440;

    try {
      const resp = await fetch('/api/v1/knowledge-graph');
      const data = await resp.json();
      renderLivingGraphCanvas(ctx, canvas.width, canvas.height, data);
    } catch (err) {
      console.warn('Failed to load living graph:', err);
    }
  }

  function renderLivingGraphCanvas(ctx, w, h, data) {
    ctx.clearRect(0, 0, w, h);
    const cx = w / 2;
    const cy = h / 2;

    const nodePositions = {};
    const nodes = data.nodes || [];
    const edges = data.edges || [];

    nodes.forEach((n, idx) => {
      const angle = (idx / nodes.length) * Math.PI * 2;
      const radiusDist = idx === 0 ? 0 : 130 + (idx % 2 === 0 ? 30 : -20);
      const x = cx + Math.cos(angle) * radiusDist;
      const y = cy + Math.sin(angle) * radiusDist;
      nodePositions[n.id] = { ...n, x, y };
    });

    // Draw Edges
    edges.forEach(e => {
      const src = nodePositions[e.source];
      const tgt = nodePositions[e.target];
      if (src && tgt) {
        ctx.beginPath();
        ctx.moveTo(src.x, src.y);
        ctx.lineTo(tgt.x, tgt.y);
        ctx.strokeStyle = e.relation.includes('FABRICATE') ? 'rgba(239, 68, 68, 0.4)' : 'rgba(94, 75, 245, 0.35)';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Edge label
        ctx.font = '9px sans-serif';
        ctx.fillStyle = '#94A3B8';
        ctx.fillText(e.relation, (src.x + tgt.x) / 2, (src.y + tgt.y) / 2);
      }
    });

    // Draw Nodes
    Object.values(nodePositions).forEach(n => {
      ctx.beginPath();
      ctx.arc(n.x, n.y, 14, 0, Math.PI * 2);
      ctx.fillStyle = n.trust_score >= 0.8 ? '#10B981' : (n.trust_score <= 0.3 ? '#EF4444' : '#5E4BF5');
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.font = '11px sans-serif';
      ctx.fillStyle = '#1E293B';
      ctx.fillText(n.name, n.x, n.y + 24);
    });
  }

  // ==========================================
  // TAB 5: DEEP VERIFY (Existing Core Engine)
  // ==========================================
  const inputTextInput = document.getElementById('input-text');
  const publisherInput = document.getElementById('input-publisher');
  const verifyBtn = document.getElementById('btn-execute-verify');
  const urlScrapeBtn = document.getElementById('btn-url-scrape');
  const inputUrlField = document.getElementById('input-url');

  if (urlScrapeBtn && inputUrlField) {
    urlScrapeBtn.addEventListener('click', async () => {
      const url = inputUrlField.value.trim();
      if (!url) return alert('Please enter a valid article URL');

      urlScrapeBtn.innerText = 'Scraping...';
      urlScrapeBtn.disabled = true;

      try {
        const resp = await fetch('/api/v1/scrape', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url }),
        });
        const data = await resp.json();
        if (data.status === 'success') {
          inputTextInput.value = data.body_text;
          publisherInput.value = data.domain;
          inputUrlField.value = '';
          executeVerification();
        } else {
          alert('Failed to parse URL: ' + (data.error || 'Unknown error'));
        }
      } catch (err) {
        alert('Network error while scraping URL: ' + err.message);
      } finally {
        urlScrapeBtn.innerText = 'Extract & Verify';
        urlScrapeBtn.disabled = false;
      }
    });
  }

  window.loadSample = function (type) {
    if (type === 'microchip') {
      inputTextInput.value = 'Viral social media posts claim COVID-19 vaccines contain secret microchips designed for human tracking.';
      publisherInput.value = 'dailyconspiracy.net';
    } else if (type === 'isro') {
      inputTextInput.value = 'Scientists at ISRO confirmed that the Pragyan rover analyzed lunar soil and detected sulfur near the south pole.';
      publisherInput.value = 'pib.gov.in';
    } else if (type === 'satire') {
      inputTextInput.value = 'NASA Announces Plans To Colonize Sun At Night To Avoid Burning Up.';
      publisherInput.value = 'theonion.com';
    }
    executeVerification();
  };

  async function executeVerification() {
    const text = inputTextInput?.value.trim();
    const publisher = publisherInput?.value.trim();
    if (!text) return;

    if (verifyBtn) {
      verifyBtn.innerText = 'Analyzing Pipeline...';
      verifyBtn.disabled = true;
    }

    try {
      const resp = await fetch('/api/v1/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, publisher: publisher || null }),
      });
      const data = await resp.json();
      state.latestResult = data;
      state.claims = data.claims || [];
      state.selectedClaimIndex = 0;

      renderVerificationResults(data);
    } catch (err) {
      alert('Verification API error: ' + err.message);
    } finally {
      if (verifyBtn) {
        verifyBtn.innerText = 'Run Tri-Modal Verification';
        verifyBtn.disabled = false;
      }
    }
  }

  const verifyForm = document.getElementById('verify-form');
  if (verifyForm) {
    verifyForm.addEventListener('submit', (e) => {
      e.preventDefault();
      executeVerification();
    });
  }

  function renderVerificationResults(result) {
    const cardGrounding = document.getElementById('metric-grounding');
    const cardFreshness = document.getElementById('metric-freshness');
    const cardRisk = document.getElementById('metric-risk');
    const cardVerdict = document.getElementById('metric-verdict');

    if (result.nutrition_card) {
      if (cardGrounding) cardGrounding.innerText = `${result.nutrition_card.factual_grounding_score}%`;
      if (cardFreshness) cardFreshness.innerText = `w(t) = ${(result.nutrition_card.temporal_freshness_score / 100).toFixed(2)}`;
    }
    if (cardRisk) cardRisk.innerText = `${(result.graph_anomaly_score * 100).toFixed(0)}%`;
    if (cardVerdict) {
      cardVerdict.innerText = result.verdict;
      cardVerdict.className = 'text-2xl font-bold tabular ' + (
        result.verdict === 'REAL' ? 'text-emerald-600' : (result.verdict === 'FAKE' ? 'text-rose-600' : 'text-amber-500')
      );
    }

    const claimsContainer = document.getElementById('claims-list-container');
    if (!claimsContainer) return;
    claimsContainer.innerHTML = '';

    if (!result.claims || result.claims.length === 0) {
      claimsContainer.innerHTML = '<div class="text-slate-400 p-4">No atomic assertions detected.</div>';
    } else {
      result.claims.forEach((claim, idx) => {
        const item = document.createElement('div');
        item.className = `p-3 rounded-xl cursor-pointer transition flex items-start gap-3 ${
          idx === state.selectedClaimIndex ? 'bg-[#282161] border border-indigo-400/30' : 'bg-[#181D2A] hover:bg-[#1E2435]'
        }`;

        let badgeColor = 'bg-amber-500/20 text-amber-300';
        let badgeIcon = '🟡 [DATA-VOID]';
        if (claim.highlight_status === 'VERIFIED') {
          badgeColor = 'bg-emerald-500/20 text-emerald-300';
          badgeIcon = '🟢 [VERIFIED]';
        } else if (claim.highlight_status === 'REFUTED') {
          badgeColor = 'bg-rose-500/20 text-rose-300';
          badgeIcon = '🔴 [REFUTED]';
        }

        item.innerHTML = `
          <div class="mt-0.5"><span class="text-xs px-2 py-0.5 rounded-full font-medium ${badgeColor}">${badgeIcon}</span></div>
          <div class="flex-1 min-w-0">
            <p class="text-sm text-slate-100 font-medium line-clamp-2 leading-relaxed">"${claim.text}"</p>
            <div class="flex items-center gap-2 mt-1 text-xs text-slate-400">
              <span>Worthiness: ${claim.check_worthiness}</span>
              <span>•</span>
              <span class="capitalize">${claim.domain || 'general'}</span>
            </div>
          </div>
        `;

        item.addEventListener('click', () => {
          state.selectedClaimIndex = idx;
          renderVerificationResults(state.latestResult);
        });

        claimsContainer.appendChild(item);
      });
    }

    renderActiveClaimDetail();
  }

  function renderActiveClaimDetail() {
    const detailBox = document.getElementById('active-claim-detail');
    if (!detailBox) return;

    if (!state.latestResult || !state.claims[state.selectedClaimIndex]) {
      detailBox.innerHTML = '<div class="text-slate-400 p-8 text-center">Select an assertion to inspect primary fact-check grounding.</div>';
      return;
    }

    const claim = state.claims[state.selectedClaimIndex];
    const nCard = state.latestResult.nutrition_card;
    const matchedEvidence = (state.latestResult.alignments || []).filter(a => a.claim.text === claim.text);

    let evidenceHtml = '';
    if (matchedEvidence.length > 0) {
      evidenceHtml = matchedEvidence.map(a => `
        <div class="p-3 bg-black/25 rounded-xl border border-white/10 mt-2 text-xs">
          <div class="flex items-center justify-between text-indigo-200 font-medium mb-1">
            <span>${a.evidence.publisher}</span>
            <span class="px-2 py-0.5 rounded bg-indigo-500/30 text-white">${a.stance}</span>
          </div>
          <p class="text-slate-200 line-clamp-3">${a.evidence.snippet}</p>
          <div class="mt-2 flex items-center justify-between text-[11px] text-slate-400">
            <span>Score: ${(a.alignment_score * 100).toFixed(0)}%</span>
            ${a.evidence.url ? `<a href="${a.evidence.url}" target="_blank" class="text-indigo-300 underline hover:text-white">View Source</a>` : ''}
          </div>
        </div>
      `).join('');
    } else {
      evidenceHtml = '<p class="text-xs text-amber-200/80 italic mt-2">Zero matching records in verified IFCN registry. Strictly classified as DATA_VOID without assuming.</p>';
    }

    detailBox.innerHTML = `
      <div class="flex items-start justify-between gap-3">
        <div>
          <span class="text-xs uppercase tracking-wider text-indigo-300 font-semibold">Assertion #${claim.index + 1}</span>
          <h4 class="text-base font-semibold text-white mt-1">"${claim.text}"</h4>
        </div>
        <span class="text-xs px-2.5 py-1 rounded-full bg-white/10 text-white font-mono">${state.latestResult.latency_ms} ms</span>
      </div>

      <div class="mt-4 pt-3 border-t border-white/10">
        <span class="text-xs font-semibold text-indigo-200 uppercase tracking-wide">Accredited Evidence Grounding</span>
        ${evidenceHtml}
      </div>

      ${nCard ? `
        <div class="mt-4 pt-3 border-t border-white/10">
          <span class="text-xs font-semibold text-indigo-200 uppercase tracking-wide mb-2 block">Contextual Nutrition Card</span>
          <div class="radar-grid text-xs">
            <div class="radar-item">
              <span class="text-slate-300 block text-[11px]">Factual Grounding</span>
              <span class="text-base font-bold text-white tabular">${nCard.factual_grounding_score}%</span>
            </div>
            <div class="radar-item">
              <span class="text-slate-300 block text-[11px]">Source Transparency</span>
              <span class="text-base font-bold text-white tabular">${nCard.source_transparency_score}%</span>
            </div>
            <div class="radar-item">
              <span class="text-slate-300 block text-[11px]">Organic Diffusion</span>
              <span class="text-base font-bold text-white tabular">${nCard.organic_diffusion_score}%</span>
            </div>
            <div class="radar-item">
              <span class="text-slate-300 block text-[11px]">Temporal Freshness</span>
              <span class="text-base font-bold text-white tabular">${nCard.temporal_freshness_score}%</span>
            </div>
          </div>
        </div>
      ` : ''}
    `;
  }

  // ==========================================
  // TAB 6: CASCADES RADAR
  // ==========================================
  async function initCascadePage() {
    try {
      const resp = await fetch('/api/v1/cascades/sample');
      const cascadeData = await resp.json();
      state.graphVisualizer = new window.CascadeGraphVisualizer('cascade-canvas');
      state.graphVisualizer.loadCascade(cascadeData);
    } catch (err) {
      console.warn('Failed to load cascade sample:', err);
    }
  }

  // ==========================================
  // TAB 7: COMMUNITY NOTES
  // ==========================================
  const submitVoteBtn = document.getElementById('btn-submit-vote');
  if (submitVoteBtn) {
    submitVoteBtn.addEventListener('click', async () => {
      const selectedRating = parseFloat(document.querySelector('input[name="vote-rating"]:checked')?.value || '1.0');
      const ratingsPayload = [
        { rater_id: 'u_left_1', note_id: 'note_101', rating: 1.0 },
        { rater_id: 'u_left_2', note_id: 'note_101', rating: 1.0 },
        { rater_id: 'u_right_1', note_id: 'note_101', rating: 1.0 },
        { rater_id: 'u_right_2', note_id: 'note_101', rating: 1.0 },
        { rater_id: 'user_active', note_id: 'note_101', rating: selectedRating },
      ];

      try {
        const resp = await fetch('/api/v1/consensus/score', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ratings: ratingsPayload }),
        });
        const scores = await resp.json();
        const res = scores['note_101'];

        document.getElementById('consensus-status-badge').innerText = res.status;
        document.getElementById('consensus-helpfulness-score').innerText = `b_i = ${res.helpfulness_score.toFixed(3)}`;
        alert(`Bipartisan consensus calculated: Intercept b_i = ${res.helpfulness_score}`);
      } catch (err) {
        alert('Consensus scoring failed: ' + err.message);
      }
    });
  }

  // Auth / Role modal
  window.openAuthModal = function () {
    if (authModal) authModal.classList.remove('hidden');
  };
  window.closeAuthModal = function () {
    if (authModal) authModal.classList.add('hidden');
  };
  window.selectRole = function (roleName) {
    state.currentRole = roleName;
    if (roleBadge) roleBadge.innerText = roleName.toUpperCase();
    closeAuthModal();
  };

  initRouting();
});
