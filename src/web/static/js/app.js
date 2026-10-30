/**
 * TruthLens-Omni Single Page Application Core Controller.
 * Manages 5 core operational pages, auth modal, profile, and real-time backend API bindings.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Application State
  const state = {
    activeTab: 'verify',
    currentRole: 'journalist',
    claims: [],
    selectedClaimIndex: 0,
    latestResult: null,
    graphVisualizer: null,
  };

  // DOM Elements
  const tabButtons = document.querySelectorAll('.nav-tab-btn');
  const pageSections = document.querySelectorAll('.page-view');
  const roleBadge = document.getElementById('user-role-badge');
  const authModal = document.getElementById('auth-modal');

  // Initialize Route
  function initRouting() {
    const hash = window.location.hash.replace('#', '') || 'verify';
    switchTab(hash);

    window.addEventListener('hashchange', () => {
      const target = window.location.hash.replace('#', '') || 'verify';
      switchTab(target);
    });
  }

  // Switch Active Operational Page
  function switchTab(tabName) {
    if (!['landing', 'verify', 'cascades', 'consensus', 'multimodal', 'trends', 'profile'].includes(tabName)) {
      tabName = 'verify';
    }
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

    // Update Page View Visibility
    pageSections.forEach((section) => {
      if (section.id === `page-${tabName}`) {
        section.classList.remove('hidden');
      } else {
        section.classList.add('hidden');
      }
    });

    // Lazy initialization for specific page needs
    if (tabName === 'cascades' && !state.graphVisualizer) {
      setTimeout(() => initCascadePage(), 100);
    }
  }

  tabButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const target = btn.getAttribute('data-tab');
      switchTab(target);
    });
  });

  // ==========================================
  // PAGE 1: DEEP VERIFICATION STUDIO
  // ==========================================
  const verifyForm = document.getElementById('verify-form');
  const inputTextInput = document.getElementById('input-text');
  const publisherInput = document.getElementById('input-publisher');
  const verifyBtn = document.getElementById('btn-execute-verify');
  const urlScrapeBtn = document.getElementById('btn-url-scrape');
  const inputUrlField = document.getElementById('input-url');

  // Handle URL 1-Click Scraping (Feature 10)
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
          // Trigger immediate verification
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

  // Sample Claim Click Handler
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
    const text = inputTextInput.value.trim();
    const publisher = publisherInput.value.trim();
    if (!text) return;

    verifyBtn.innerText = 'Analyzing Pipeline...';
    verifyBtn.disabled = true;

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
      verifyBtn.innerText = 'Run Tri-Modal Verification';
      verifyBtn.disabled = false;
    }
  }

  if (verifyForm) {
    verifyForm.addEventListener('submit', (e) => {
      e.preventDefault();
      executeVerification();
    });
  }

  function renderVerificationResults(result) {
    // 1. Update Top 4 Metric Cards
    const cardGrounding = document.getElementById('metric-grounding');
    const cardFreshness = document.getElementById('metric-freshness');
    const cardRisk = document.getElementById('metric-risk');
    const cardVerdict = document.getElementById('metric-verdict');

    if (result.nutrition_card) {
      cardGrounding.innerText = `${result.nutrition_card.factual_grounding_score}%`;
      cardFreshness.innerText = `w(t) = ${(result.nutrition_card.temporal_freshness_score / 100).toFixed(2)}`;
    }
    cardRisk.innerText = `${(result.graph_anomaly_score * 100).toFixed(0)}%`;
    cardVerdict.innerText = result.verdict;

    // Verdict Badge coloring
    cardVerdict.className = 'text-2xl font-bold tabular ' + (
      result.verdict === 'REAL' ? 'text-emerald-600' : (result.verdict === 'FAKE' ? 'text-rose-600' : 'text-amber-500')
    );

    // 2. Render Left Claim List (Feature 2)
    const claimsContainer = document.getElementById('claims-list-container');
    claimsContainer.innerHTML = '';

    if (!result.claims || result.claims.length === 0) {
      claimsContainer.innerHTML = '<div class="text-slate-400 p-4">No atomic factual assertions detected.</div>';
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

    // 3. Render Right Detail Card (Nutrition Card + Evidence)
    renderActiveClaimDetail();
  }

  function renderActiveClaimDetail() {
    const detailBox = document.getElementById('active-claim-detail');
    if (!state.latestResult || !state.claims[state.selectedClaimIndex]) {
      detailBox.innerHTML = '<div class="text-slate-400 p-8 text-center">Select an extracted claim to inspect primary fact-check grounding.</div>';
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
            ${a.evidence.url ? `<a href="${a.evidence.url}" target="_blank" class="text-indigo-300 underline hover:text-white">View Fact-Check Link</a>` : ''}
          </div>
        </div>
      `).join('');
    } else {
      evidenceHtml = '<p class="text-xs text-amber-200/80 italic mt-2">Zero matching records in verified IFCN registry. Strictly classified as DATA_VOID without assuming.</p>';
    }

    detailBox.innerHTML = `
      <div class="flex items-start justify-between gap-3">
        <div>
          <span class="text-xs uppercase tracking-wider text-indigo-300 font-semibold">Active Claim Assertion #${claim.index + 1}</span>
          <h4 class="text-base font-semibold text-white mt-1">"${claim.text}"</h4>
        </div>
        <span class="text-xs px-2.5 py-1 rounded-full bg-white/10 text-white font-mono">${state.latestResult.latency_ms} ms</span>
      </div>

      <div class="mt-4 pt-3 border-t border-white/10">
        <span class="text-xs font-semibold text-indigo-200 uppercase tracking-wide">Accredited Evidence Grounding (CEAM)</span>
        ${evidenceHtml}
      </div>

      ${nCard ? `
        <div class="mt-4 pt-3 border-t border-white/10">
          <span class="text-xs font-semibold text-indigo-200 uppercase tracking-wide mb-2 block">Contextual Nutrition Card (Feature 1)</span>
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

      <div class="mt-4 pt-3 border-t border-white/10 flex items-center justify-between">
        <span class="text-xs text-slate-300">Auditable Ground-Truth Pipeline</span>
        <button onclick="window.location.hash='consensus'" class="px-3 py-1.5 rounded-lg bg-white/15 hover:bg-white/25 text-white text-xs font-medium transition">
          Seed into Community Notes →
        </button>
      </div>
    `;
  }

  // ==========================================
  // PAGE 2: SOCIAL CASCADES & CIB RADAR
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
  // PAGE 3: COMMUNITY BRIDGING CONSENSUS HUB
  // ==========================================
  const submitVoteBtn = document.getElementById('btn-submit-vote');
  if (submitVoteBtn) {
    submitVoteBtn.addEventListener('click', async () => {
      const selectedRating = parseFloat(document.querySelector('input[name="vote-rating"]:checked')?.value || '1.0');
      const raterId = 'user_current_' + state.currentRole;

      const ratingsPayload = [
        { rater_id: 'u_left_1', note_id: 'note_101', rating: 1.0 },
        { rater_id: 'u_left_2', note_id: 'note_101', rating: 1.0 },
        { rater_id: 'u_right_1', note_id: 'note_101', rating: 1.0 },
        { rater_id: 'u_right_2', note_id: 'note_101', rating: 1.0 },
        { rater_id: raterId, note_id: 'note_101', rating: selectedRating },
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
        alert(`Vote recorded! Matrix Factorization re-computed note helpfulness intercept: b_i = ${res.helpfulness_score}`);
      } catch (err) {
        alert('Consensus scoring failed: ' + err.message);
      }
    });
  }

  // ==========================================
  // AUTH MODAL & ROLE SELECTOR
  // ==========================================
  window.openAuthModal = function () {
    if (authModal) authModal.classList.remove('hidden');
  };

  window.closeAuthModal = function () {
    if (authModal) authModal.classList.add('hidden');
  };

  window.selectRole = function (roleName) {
    state.currentRole = roleName;
    if (roleBadge) {
      roleBadge.innerText = roleName.toUpperCase();
    }
    closeAuthModal();
    alert(`Switched to active role: ${roleName.toUpperCase()}`);
  };

  // Initialize
  initRouting();
  // Trigger initial sample for immediate pitch demonstration
  window.loadSample('microchip');
});
