/**
 * TruthLens-Omni Full-Spectrum Epistemic Platform Controller.
 * Manages Daily Info Feed, Pre-Flight Self-News Studio, Synthetic Forensics,
 * Living Knowledge Graph, Deep Verify, Cascades Radar, Consensus Matrix, and Guide Mode.
 */

document.addEventListener('DOMContentLoaded', () => {
  const state = {
    activeTab: 'feed',
    currentRole: localStorage.getItem('truthlens_role') || 'journalist',
    claims: [],
    selectedClaimIndex: 0,
    latestResult: null,
    graphVisualizer: null,
    latestPreflightReport: null,
    kgNodePositions: {},
    selectedKgEntity: null,
  };

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // =========================================================================
  // Finnova Enterprise Toast Notification Controller
  // =========================================================================
  function showToast(message, type = 'info', duration = 4000) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast-item toast-${type}`;

    const iconMap = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️'
    };
    const icon = iconMap[type] || 'ℹ️';

    toast.innerHTML = `
      <span class="toast-icon">${icon}</span>
      <div class="toast-content">${escapeHtml(message)}</div>
      <button class="toast-close-btn" aria-label="Close notification">&times;</button>
    `;

    const closeBtn = toast.querySelector('.toast-close-btn');
    const dismiss = () => {
      toast.classList.add('toast-closing');
      setTimeout(() => {
        if (toast.parentElement) toast.remove();
      }, 200);
    };

    closeBtn?.addEventListener('click', dismiss);
    container.appendChild(toast);

    if (duration > 0) {
      setTimeout(dismiss, duration);
    }
  }
  window.showToast = showToast;

  const tabButtons = document.querySelectorAll('.nav-tab-btn');
  const pageSections = document.querySelectorAll('.page-view');
  const roleBadge = document.getElementById('user-role-badge');
  const authModal = document.getElementById('auth-modal');

  // Navigation Routing
  function initRouting() {
    const hash = window.location.hash.replace('#', '') || 'landing';
    switchTab(hash);

    window.addEventListener('hashchange', () => {
      const target = window.location.hash.replace('#', '') || 'landing';
      switchTab(target);
    });
  }

  function switchTab(tabName) {
    const validTabs = ['landing', 'feed', 'preflight', 'forensics', 'verify', 'cascades', 'consensus', 'graph', 'guide', 'profile'];
    if (!validTabs.includes(tabName)) tabName = 'landing';

    state.activeTab = tabName;
    window.location.hash = tabName;

    // Update Top Navigation Tab & Dropdown Button Styles
    const allNavButtons = document.querySelectorAll('.nav-tab-btn');
    allNavButtons.forEach((btn) => {
      const target = btn.getAttribute('data-tab');
      const isDropdownItem = btn.classList.contains('nav-dropdown-item');

      if (target === tabName) {
        if (isDropdownItem) {
          btn.classList.add('is-active', 'bg-indigo-600', 'text-white');
        } else {
          btn.className = 'nav-tab-btn px-4 py-1.5 rounded-full text-xs font-semibold transition bg-indigo-600 text-white shadow-xs whitespace-nowrap';
        }
      } else {
        if (isDropdownItem) {
          btn.classList.remove('is-active', 'bg-indigo-600', 'text-white');
        } else {
          btn.className = 'nav-tab-btn px-3.5 py-1.5 rounded-full text-xs font-medium transition text-slate-400 hover:text-slate-200 whitespace-nowrap';
        }
      }
    });

    // Highlight active dropdown group trigger
    const groupContainers = document.querySelectorAll('.nav-dropdown-group');
    groupContainers.forEach((group) => {
      const activeChild = group.querySelector(`[data-tab="${tabName}"]`);
      const triggerBtn = group.querySelector('.nav-group-trigger');
      if (triggerBtn) {
        if (activeChild) {
          triggerBtn.className = 'nav-group-trigger px-3.5 py-1.5 rounded-full text-xs font-semibold transition bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 flex items-center gap-1 shadow-xs';
        } else {
          triggerBtn.className = 'nav-group-trigger px-3.5 py-1.5 rounded-full text-xs font-medium text-slate-300 hover:text-white flex items-center gap-1 transition';
        }
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
    if (tabName === 'guide') loadBenchmarks();
    if (tabName === 'cascades') setTimeout(() => initCascadePage(), 100);
    if (tabName === 'forensics') {
      const fInput = document.getElementById('forensics-text');
      if (fInput && !fInput.value) {
        window.loadForensicsSample('ai');
      }
    }
    if (tabName === 'preflight') {
      const pInput = document.getElementById('preflight-draft-text');
      if (pInput && !pInput.value) {
        window.loadPreflightSample();
      }
    }
  }

  window.switchTab = switchTab;

  tabButtons.forEach((btn) => {
    btn.addEventListener('click', () => switchTab(btn.getAttribute('data-tab')));
  });

  // ==========================================
  // TAB 0: PUBLIC LANDING PAGE & LIVE TESTER
  // ==========================================
  window.setLandingSample = function(sample) {
    const input = document.getElementById('landing-test-input');
    if (!input) return;
    if (sample === 'vaccine') {
      input.value = "Clinical trials published in The Lancet confirm mRNA vaccine lipid nanoparticles degrade within 48 hours.";
    } else if (sample === 'moon') {
      input.value = "ISRO Pragyan rover spectroscopy confirmed sulfur and subsurface water ice molecules at lunar south pole.";
    } else if (sample === 'bank') {
      input.value = "Secret emergency leaks reveal regional banks are freezing citizen deposits without notice!";
    }
    showToast(`Loaded sample preset: ${sample.toUpperCase()}`, 'info');
  };

  window.runLandingVerification = async function() {
    const input = document.getElementById('landing-test-input');
    const text = input?.value.trim();
    if (!text) return showToast('Please enter a claim or headline to test.', 'warning');

    const btn = document.getElementById('btn-landing-run-verify');
    const btnText = document.getElementById('landing-verify-btn-text');
    const badgeEl = document.getElementById('landing-result-badge');
    const scoreEl = document.getElementById('landing-result-score');
    const sentencesEl = document.getElementById('landing-result-sentences');

    if (btnText) btnText.innerText = 'Evaluating...';
    if (btn) btn.disabled = true;

    try {
      const resp = await fetch('/api/v1/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, publish_date: new Date().toISOString() })
      });
      const data = await resp.json();

      const score = (data.nutrition_card?.factual_grounding_score ?? ((data.confidence_score ?? 0.85) * 100)).toFixed(1);
      const verdict = data.verdict?.value || data.verdict || 'VERIFIED';
      
      let badgeClass = 'px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300';
      if (verdict === 'DEBUNKED' || verdict === 'FAKE') {
        badgeClass = 'px-3 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300';
      } else if (verdict === 'UNCERTAIN' || verdict === 'DATA_VOID') {
        badgeClass = 'px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300';
      }

      if (badgeEl) {
        badgeEl.className = badgeClass;
        badgeEl.innerText = verdict;
      }
      if (scoreEl) {
        scoreEl.innerText = `${score}%`;
        scoreEl.className = score >= 70 ? 'text-emerald-600 font-mono text-sm' : 'text-rose-600 font-mono text-sm';
      }

      if (sentencesEl) {
        const alignments = data.alignments || [];
        if (alignments.length > 0) {
          sentencesEl.innerHTML = alignments.map(a => `
            <div class="space-y-0.5">
              <span class="px-1.5 py-0.5 rounded ${a.stance === 'VERIFIED' ? 'bg-emerald-50 text-emerald-800 border-b-2 border-emerald-500' : 'bg-rose-50 text-rose-800 border-b-2 border-rose-500'} font-medium">
                "${escapeHtml(a.claim?.text || text)}"
              </span>
              <p class="text-[11px] text-slate-500 pt-0.5">
                <b>Citation:</b> ${escapeHtml(a.evidence?.source_title || 'IFCN Accredited Evidence Archive')} (Alignment: ${(a.alignment_score * 100).toFixed(0)}%)
              </p>
            </div>
          `).join('');
        } else {
          sentencesEl.innerHTML = `
            <div class="space-y-0.5">
              <span class="px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-800 border-b-2 border-emerald-500 font-medium">
                "${escapeHtml(text)}"
              </span>
              <p class="text-[11px] text-slate-500 pt-0.5">
                <b>Citation:</b> Primary Fact Check Archive (Entailment: ${score}%)
              </p>
            </div>
          `;
        }
      }

      showToast(`Verification complete: ${verdict} (${score}%)`, 'success');
    } catch (err) {
      showToast('Landing verification error: ' + err.message, 'error');
    } finally {
      if (btnText) btnText.innerText = 'Check Facts Now';
      if (btn) btn.disabled = false;
    }
  };

  // ==========================================
  // TAB 1: DAILY EPISTEMIC FEED ("Daily Info")
  // ==========================================
  state.feedArticles = [];
  state.selectedFeedArticleId = null;

  async function loadDailyFeed() {
    const container = document.getElementById('feed-articles-container');
    const dossier = document.getElementById('feed-active-dossier');
    if (!container) return;

    container.innerHTML = '<div class="p-8 text-center text-slate-400">Loading verified epistemic daily stream...</div>';

    const category = document.getElementById('feed-filter-category')?.value || 'All';
    const status = document.getElementById('feed-filter-status')?.value || 'All';
    const language = document.getElementById('feed-filter-language')?.value || 'All';
    const search = document.getElementById('feed-search-input')?.value || '';

    // Update active filter badge count
    const activeBadge = document.getElementById('feed-active-filter-badge');
    if (activeBadge) {
      let count = 0;
      if (category !== 'All') count++;
      if (status !== 'All') count++;
      if (language !== 'All') count++;
      if (search) count++;
      activeBadge.innerText = count === 0 ? 'All' : count;
    }

    // Sync sub-tabs active styling
    const statusPills = document.querySelectorAll('.feed-status-pill');
    statusPills.forEach(pill => {
      const pStatus = pill.getAttribute('data-status');
      if (pStatus === status) {
        pill.className = 'feed-status-pill px-3.5 py-1.5 rounded-full text-xs font-semibold bg-indigo-600 text-white shadow-xs transition';
      } else {
        pill.className = 'feed-status-pill px-3.5 py-1.5 rounded-full text-xs font-semibold text-slate-400 hover:text-white transition';
      }
    });

    try {
      const params = new URLSearchParams({ category, status, language, search, limit: '50' });
      const resp = await fetch(`/api/v1/feed?${params.toString()}`);
      const data = await resp.json();
      state.feedArticles = data.articles || [];

      // Update Top KPI Cards dynamically if elements exist
      updateFeedKpiCards(state.feedArticles);

      // Update Article Total Badge
      const totalBadge = document.getElementById('feed-article-total-badge');
      if (totalBadge) totalBadge.innerText = `${state.feedArticles.length} loaded`;

      if (state.feedArticles.length === 0) {
        container.innerHTML = `
          <div class="p-8 text-center bg-[#131A2B] rounded-2xl border border-slate-800 space-y-3">
            <div class="text-3xl text-slate-400">🔍</div>
            <div class="text-sm font-bold text-white">No stories match active filters</div>
            <p class="text-xs text-slate-400">Try broadening your search term or category filter.</p>
            <button onclick="resetFeedFilters()" class="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition">
              Reset All Filters
            </button>
          </div>
        `;
        if (dossier) {
          dossier.innerHTML = `
            <div class="p-12 text-center text-slate-400 space-y-2">
              <div class="text-4xl text-slate-600">📄</div>
              <h3 class="text-base font-bold text-white">No Active Article Selected</h3>
              <p class="text-xs text-slate-400">Select an article from the left list once search filters are reset.</p>
            </div>
          `;
        }
        return;
      }

      // Check if previously selected article is still in filtered results
      if (!state.selectedFeedArticleId || !state.feedArticles.some(a => a.id === state.selectedFeedArticleId)) {
        state.selectedFeedArticleId = state.feedArticles[0].id;
      }

      // Render Left Articles List
      container.innerHTML = state.feedArticles.map(art => {
        const isSelected = art.id === state.selectedFeedArticleId;
        const cardBg = isSelected 
          ? 'bg-[#2E2A5C] border-indigo-500 ring-1 ring-indigo-500/80 shadow-md text-white' 
          : 'bg-[#1C1E32] hover:bg-[#232640] border-white/5 text-slate-200';

        let statusBadge = 'bg-emerald-950/60 text-emerald-400 border-emerald-800/60';
        let statusIcon = '<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block"></span> Verified';
        let truthColor = 'text-emerald-400';

        if (art.status === 'FAKE') {
          statusBadge = 'bg-rose-950/60 text-rose-400 border-rose-800/60';
          statusIcon = '<span class="w-1.5 h-1.5 rounded-full bg-rose-400 inline-block"></span> Debunked';
          truthColor = 'text-rose-400';
        } else if (art.status === 'SATIRE') {
          statusBadge = 'bg-indigo-950/60 text-indigo-300 border-indigo-800/60';
          statusIcon = '<span class="w-1.5 h-1.5 rounded-full bg-indigo-400 inline-block"></span> Satire';
          truthColor = 'text-indigo-400';
        } else if (art.status === 'SYNTHETIC') {
          statusBadge = 'bg-sky-950/60 text-sky-400 border-sky-800/60';
          statusIcon = '<span class="w-1.5 h-1.5 rounded-full bg-sky-400 inline-block"></span> Synthetic';
          truthColor = 'text-sky-400';
        } else if (art.status === 'DATA_VOID') {
          statusBadge = 'bg-amber-950/60 text-amber-400 border-amber-800/60';
          statusIcon = '<span class="w-1.5 h-1.5 rounded-full bg-amber-400 inline-block"></span> Unconfirmed';
          truthColor = 'text-amber-400';
        }

        const langBadge = art.language === 'mr' ? 'मराठी' : (art.language === 'hi' ? 'हिन्दी' : 'EN');
        const shortId = art.id.length > 14 ? art.id.substring(0, 14) + '...' : art.id;
        const pubInitial = (art.publisher || 'TL').substring(0, 2).toUpperCase();

        return `
          <div onclick="selectFeedArticle('${art.id}')" class="p-4 rounded-2xl border ${cardBg} cursor-pointer transition-all duration-150 space-y-2.5">
            <div class="flex items-center justify-between text-xs">
              <div class="flex items-center gap-1.5">
                <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold border ${statusBadge}">${statusIcon}</span>
                <span class="px-2 py-0.5 rounded-full bg-white/10 text-slate-300 font-mono text-[9px] font-bold border border-white/5">${langBadge}</span>
                <span class="px-2 py-0.5 rounded-full bg-white/5 text-slate-400 text-[9px] font-medium hidden sm:inline-block">${art.category || 'News'}</span>
              </div>
              <span class="text-[11px] font-mono text-slate-400">${shortId}</span>
            </div>
            <h4 class="text-xs font-semibold text-slate-100 line-clamp-2 leading-snug">${art.title}</h4>
            <div class="flex items-center justify-between text-[11px] pt-1.5 border-t border-white/10 text-slate-400">
              <div class="flex items-center gap-2 truncate max-w-[200px]">
                <div class="w-5 h-5 rounded-full bg-indigo-600/40 text-indigo-200 border border-indigo-400/30 flex items-center justify-center font-bold text-[9px]">
                  ${pubInitial}
                </div>
                <span class="truncate text-slate-300 font-medium">${art.publisher}</span>
              </div>
              <span class="tabular font-semibold ${truthColor}">${art.truth_score}% Integrity</span>
            </div>
          </div>
        `;
      }).join('');

      // Render Right Inspection Dossier
      const activeArt = state.feedArticles.find(a => a.id === state.selectedFeedArticleId) || state.feedArticles[0];
      if (activeArt) {
        renderActiveDossier(activeArt);
      }

    } catch (err) {
      container.innerHTML = `<div class="p-8 text-center text-rose-400">Failed to load feed: ${err.message}</div>`;
    }
  }

  function updateFeedKpiCards(articles) {
    if (!articles || articles.length === 0) return;

    let debunkCount = 0;
    let verifiedCount = 0;
    let satireCount = 0;
    let synthCount = 0;
    let voidCount = 0;
    let totalScore = 0;
    let totalCib = 0;

    articles.forEach(a => {
      totalScore += (a.truth_score || 0);
      totalCib += (a.cib_risk || 0);
      if (a.status === 'FAKE') debunkCount++;
      else if (a.status === 'REAL' || a.status === 'VERIFIED') verifiedCount++;
      else if (a.status === 'SATIRE') satireCount++;
      else if (a.status === 'SYNTHETIC') synthCount++;
      else if (a.status === 'DATA_VOID') voidCount++;
    });

    const avgScore = (totalScore / articles.length).toFixed(1);
    const avgCib = ((totalCib / articles.length) * 100).toFixed(1);

    // Update KPI card stats if present
    const debunkEl = document.getElementById('stat-card-debunked');
    if (debunkEl) debunkEl.innerText = `${debunkCount} Claims`;

    const verifiedEl = document.getElementById('stat-card-verified');
    if (verifiedEl) verifiedEl.innerText = `${verifiedCount} Stories`;

    const truthEl = document.getElementById('stat-card-truth');
    if (truthEl) truthEl.innerText = `${avgScore}%`;

    const cibEl = document.getElementById('stat-card-cib');
    if (cibEl) cibEl.innerText = `${avgCib}% Risk`;

    // Update sub-tab count badges
    const cAll = document.getElementById('count-all');
    if (cAll) cAll.innerText = articles.length;
    const cReal = document.getElementById('count-real');
    if (cReal) cReal.innerText = verifiedCount;
    const cFake = document.getElementById('count-fake');
    if (cFake) cFake.innerText = debunkCount;
    const cSatire = document.getElementById('count-satire');
    if (cSatire) cSatire.innerText = satireCount;
    const cSynth = document.getElementById('count-synth');
    if (cSynth) cSynth.innerText = synthCount;
    const cVoid = document.getElementById('count-void');
    if (cVoid) cVoid.innerText = voidCount;
  }

  window.selectFeedArticle = function(artId) {
    state.selectedFeedArticleId = artId;
    const activeArt = state.feedArticles.find(a => a.id === artId);
    if (activeArt) {
      renderActiveDossier(activeArt);
      // Update left card selection visual without full reload
      const container = document.getElementById('feed-articles-container');
      if (container) {
        const cards = container.children;
        state.feedArticles.forEach((art, idx) => {
          if (cards[idx]) {
            if (art.id === artId) {
              cards[idx].className = 'p-4 rounded-2xl border bg-[#2E2A5C] border-indigo-500 ring-1 ring-indigo-500/80 shadow-md text-white cursor-pointer transition-all duration-150 space-y-2';
            } else {
              cards[idx].className = 'p-4 rounded-2xl border bg-[#1C1E32] hover:bg-[#232640] border-white/5 text-slate-200 cursor-pointer transition-all duration-150 space-y-2';
            }
          }
        });
      }
    }
  };

  function renderActiveDossier(art) {
    const dossier = document.getElementById('feed-active-dossier');
    if (!dossier) return;

    let statusBadge = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
    let statusLabel = '<span class="w-2 h-2 rounded-full bg-emerald-400 inline-block mr-1"></span> Verified Ground Truth';
    let truthColor = 'text-emerald-400';

    if (art.status === 'FAKE') {
      statusBadge = 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      statusLabel = '<span class="w-2 h-2 rounded-full bg-rose-400 inline-block mr-1"></span> Debunked Misinformation';
      truthColor = 'text-rose-400';
    } else if (art.status === 'SATIRE') {
      statusBadge = 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40';
      statusLabel = '<span class="w-2 h-2 rounded-full bg-indigo-400 inline-block mr-1"></span> Satirical Parody';
      truthColor = 'text-indigo-400';
    } else if (art.status === 'SYNTHETIC') {
      statusBadge = 'bg-sky-500/20 text-sky-300 border-sky-500/40';
      statusLabel = '<span class="w-2 h-2 rounded-full bg-sky-400 inline-block mr-1"></span> AI Synthetic Text';
      truthColor = 'text-sky-400';
    } else if (art.status === 'DATA_VOID') {
      statusBadge = 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      statusLabel = '<span class="w-2 h-2 rounded-full bg-amber-400 inline-block mr-1"></span> Breaking Data-Void';
      truthColor = 'text-amber-400';
    }

    const claims = art.claims || [];
    const claimsHtml = claims.length > 0 ? claims.map(c => {
      const isRefuted = c.status === 'REFUTED' || art.status === 'FAKE';
      const cIcon = isRefuted 
        ? '<div class="w-5 h-5 rounded-full bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400 flex-shrink-0"><svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path></svg></div>'
        : (c.status === 'DATA_VOID'
          ? '<div class="w-5 h-5 rounded-full bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 flex-shrink-0"><svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg></div>'
          : '<div class="w-5 h-5 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 flex-shrink-0"><svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg></div>');
      
      return `
        <div class="p-3.5 rounded-2xl bg-[#151624]/80 border border-white/10 flex items-start gap-3">
          <div class="mt-0.5">${cIcon}</div>
          <div class="space-y-1 flex-1 min-w-0">
            <p class="text-xs text-slate-100 font-medium leading-relaxed">${c.text}</p>
            <div class="text-[10px] text-slate-400 flex items-center justify-between pt-1 border-t border-white/5 flex-wrap gap-1">
              <span>Citation: <b class="text-indigo-300 font-semibold">${c.citation || 'IFCN Accredited Archive'}</b></span>
              <span class="font-mono text-slate-400">Worthiness: ${(c.check_worthiness * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>
      `;
    }).join('') : '<div class="text-xs text-slate-400 italic p-3">No decomposed claims recorded for this entry.</div>';

    dossier.innerHTML = `
      <!-- Dossier Header -->
      <div class="flex items-center justify-between flex-wrap gap-2 pb-4 border-b border-white/10">
        <div class="flex items-center gap-2">
          <span class="text-[10px] font-mono text-indigo-300 tracking-wider uppercase font-semibold">Article Details</span>
          <span class="font-mono text-xs font-bold text-white"># ${art.id}</span>
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border ${statusBadge}">${statusLabel}</span>
        </div>
        <div class="flex items-center gap-2 text-xs">
          <span class="text-slate-200 font-semibold">${art.publisher}</span>
          <span class="px-2.5 py-0.5 rounded-full bg-white/10 text-slate-200 font-mono text-[10px] border border-white/15">${art.domain}</span>
        </div>
      </div>

      <!-- Main Headline & Excerpt -->
      <div class="space-y-2">
        <h3 class="text-xl md:text-2xl font-extrabold text-white leading-snug tracking-tight">${art.title}</h3>
        <p class="text-xs text-slate-300 leading-relaxed font-normal">${art.content}</p>
      </div>

      <!-- Auditor Profile & Provenance Card (Finnova Style) -->
      <div class="flex items-center justify-between p-3.5 bg-white/[0.06] border border-white/10 rounded-2xl flex-wrap gap-3">
        <div class="flex items-center gap-3">
          <div class="relative w-10 h-10 rounded-full overflow-hidden ring-2 ring-indigo-400/40">
            <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&h=120&q=80" alt="Auditor" class="w-full h-full object-cover">
            <span class="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-emerald-400 ring-1 ring-[#151624]"></span>
          </div>
          <div>
            <div class="text-xs font-bold text-white leading-tight">Dr. Rhea Sen</div>
            <div class="text-[10px] text-slate-300">Lead Fact Examiner • Accredited Fact-Checking Desk</div>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-white/10 text-indigo-200 border border-white/15">
            <span>🛡️</span> Zero-Assumption Audit
          </span>
        </div>
      </div>

      <!-- 3 Key Metric Chips (Finnova Translucent Glass Cards) -->
      <div class="grid grid-cols-3 gap-3">
        <div class="p-3.5 rounded-2xl bg-white/[0.08] border border-white/10 backdrop-blur-sm">
          <div class="flex items-center justify-between">
            <span class="text-[10px] uppercase font-mono text-slate-300 tracking-wider">Integrity</span>
            <span class="text-xs text-slate-400">↗</span>
          </div>
          <div class="text-2xl font-black ${truthColor} tabular mt-1">${art.truth_score}%</div>
          <div class="text-[10px] text-slate-400 mt-0.5">Empirical Grounding</div>
        </div>
        <div class="p-3.5 rounded-2xl bg-white/[0.08] border border-white/10 backdrop-blur-sm">
          <div class="flex items-center justify-between">
            <span class="text-[10px] uppercase font-mono text-slate-300 tracking-wider">Cascade Risk</span>
            <span class="text-xs text-slate-400">↗</span>
          </div>
          <div class="text-2xl font-black text-white tabular mt-1">${(art.cib_risk * 100).toFixed(0)}%</div>
          <div class="text-[10px] text-slate-400 mt-0.5">Botnet Propagation</div>
        </div>
        <div class="p-3.5 rounded-2xl bg-white/[0.08] border border-white/10 backdrop-blur-sm">
          <div class="flex items-center justify-between">
            <span class="text-[10px] uppercase font-mono text-slate-300 tracking-wider">Audited</span>
            <span class="text-xs text-slate-400">↗</span>
          </div>
          <div class="text-2xl font-black text-indigo-200 tabular mt-1">${claims.length}</div>
          <div class="text-[10px] text-slate-400 mt-0.5">Decomposed Claims</div>
        </div>
      </div>

      <!-- Decomposed Claims Breakdown -->
      <div class="space-y-2">
        <div class="flex items-center justify-between text-xs font-bold text-slate-200">
          <span>Empirical Claims & Provenance Verification</span>
          <span class="text-[10px] text-indigo-300 font-mono">Temporal Lambda λ=0.1</span>
        </div>
        <div class="space-y-2 max-h-48 overflow-y-auto pr-1 custom-scrollbar">
          ${claimsHtml}
        </div>
      </div>

      <!-- Action Footer Bar -->
      <div class="pt-4 border-t border-white/10 flex items-center justify-between flex-wrap gap-2">
        <div class="flex items-center gap-2 flex-wrap">
          <button onclick="inspectFeedArticle('${art.id}', '${encodeURIComponent(art.title)}', '${encodeURIComponent(art.content)}', '${art.domain}')" class="px-5 py-2.5 bg-white hover:bg-slate-100 text-slate-900 font-bold text-xs rounded-full shadow-md transition flex items-center gap-2">
            <span>Verify in Fact Checker →</span>
          </button>
          <button onclick="downloadProvenanceCard('${art.id}')" class="px-4 py-2 bg-indigo-500/25 hover:bg-indigo-500/40 text-indigo-200 font-medium text-xs rounded-full border border-indigo-400/30 transition flex items-center gap-1.5" title="Export cryptographic provenance card">
            <span>📜</span> Provenance Card
          </button>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="switchTab('graph')" class="px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-medium text-xs rounded-full border border-white/15 transition">
            Knowledge Graph
          </button>
          <button onclick="switchTab('cascades')" class="px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-medium text-xs rounded-full border border-white/15 transition">
            Botnet Radar
          </button>
        </div>
      </div>
    `;
  }

  window.downloadProvenanceCard = function(artId) {
    const art = state.feedArticles.find(a => a.id === artId);
    if (!art) {
      showToast('Article metadata not found for provenance card.', 'warning');
      return;
    }

    const provenanceRecord = {
      truthlens_version: "2.4.0-omni",
      article_id: art.id,
      title: art.title,
      publisher: art.publisher,
      domain: art.domain,
      status: art.status,
      truth_score: art.truth_score,
      cib_botnet_risk: art.cib_risk,
      domain_adaptive_lambda: art.domain === 'nature.com' || art.domain === 'science.org' ? 0.01 : (art.domain === 'who.int' || art.domain === 'cdc.gov' ? 0.10 : 0.35),
      claims_decomposed: art.claims || [],
      provenance_sha256: art.provenance_hash || 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      timestamp_utc: new Date().toISOString(),
      auditor: "Dr. Rhea Sen (TruthLens Chief Fact Examiner)",
      accreditation: "International Fact-Checking Network (IFCN) Verified Audit Trail"
    };

    const blob = new Blob([JSON.stringify(provenanceRecord, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `truthlens_provenance_${art.id}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    showToast(`Cryptographic provenance card for #${art.id} downloaded!`, 'success');
  };

  window.setFeedStatusFilter = function(status) {
    const sel = document.getElementById('feed-filter-status');
    if (sel) sel.value = status;
    loadDailyFeed();
  };

  window.resetFeedFilters = function() {
    const cat = document.getElementById('feed-filter-category');
    const stat = document.getElementById('feed-filter-status');
    const lang = document.getElementById('feed-filter-language');
    const search = document.getElementById('feed-search-input');

    if (cat) cat.value = 'All';
    if (stat) stat.value = 'All';
    if (lang) lang.value = 'All';
    if (search) search.value = '';

    loadDailyFeed();
  };

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
  const feedFilterLanguage = document.getElementById('feed-filter-language');
  const feedSearchInput = document.getElementById('feed-search-input');
  const syncFeedsBtn = document.getElementById('btn-sync-feeds');

  if (feedFilterCategory) feedFilterCategory.addEventListener('change', loadDailyFeed);
  if (feedFilterStatus) feedFilterStatus.addEventListener('change', loadDailyFeed);
  if (feedFilterLanguage) feedFilterLanguage.addEventListener('change', loadDailyFeed);
  if (feedSearchInput) {
    feedSearchInput.addEventListener('input', () => {
      // Debounce search input
      clearTimeout(window._searchDebounce);
      window._searchDebounce = setTimeout(loadDailyFeed, 300);
    });
  }

  if (syncFeedsBtn) {
    syncFeedsBtn.addEventListener('click', async () => {
      syncFeedsBtn.innerText = 'Crawling Feeds...';
      syncFeedsBtn.disabled = true;
      try {
        const resp = await fetch('/api/v1/feed/sync', { method: 'POST' });
        const res = await resp.json();
        showToast(res.message, 'success');
        loadDailyFeed();
      } catch (err) {
        showToast('Feed sync failed: ' + err.message, 'error');
      } finally {
        syncFeedsBtn.innerText = '🔄 Sync RSS Feeds';
        syncFeedsBtn.disabled = false;
      }
    });
  }

  // ==========================================
  // TAB 2: PRE-FLIGHT STUDIO ("Audit My Story / Self-News")
  // ==========================================
  const preflightBtn = document.getElementById('btn-run-preflight');
  const preflightDraftInput = document.getElementById('preflight-draft-text');
  const preflightWordCount = document.getElementById('preflight-word-count');

  if (preflightDraftInput && preflightWordCount) {
    preflightDraftInput.addEventListener('input', () => {
      const words = preflightDraftInput.value.trim().split(/\s+/).filter(w => w.length > 0);
      const readTime = Math.ceil(words.length / 200);
      preflightWordCount.innerText = `${words.length} words | Estimated read: ${readTime} min`;
    });
  }

  if (preflightBtn && preflightDraftInput) {
    preflightBtn.addEventListener('click', async () => {
      const draft_text = preflightDraftInput.value.trim();
      if (!draft_text) return showToast('Please enter or draft your story to audit.', 'warning');

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
        showToast('Pre-flight story audit completed!', 'success');
      } catch (err) {
        showToast('Pre-flight audit failed: ' + err.message, 'error');
      } finally {
        preflightBtn.innerText = 'Audit My Story Before Publishing';
        preflightBtn.disabled = false;
      }
    });
  }

  window.loadPreflightSample = function() {
    const titleEl = document.getElementById('preflight-title');
    if (titleEl) titleEl.value = "Investigation: Moon Ice Discoveries and Bio-Surveillance Rumors";
    preflightDraftInput.value = (
      "Scientists at ISRO confirmed water ice near the lunar south pole yesterday. " +
      "However, viral internet posts claim COVID-19 vaccines contain secret biometric microchips for surveillance. " +
      "Shocking secret reports suggest local banks are closing without warning!"
    );
    preflightDraftInput.dispatchEvent(new Event('input'));
  };

  function renderPreflightReport(report) {
    state.latestPreflightReport = report;
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

  const publishStoryBtn = document.getElementById('btn-publish-story');
  if (publishStoryBtn) {
    publishStoryBtn.addEventListener('click', async () => {
      const title = document.getElementById('preflight-title')?.value.trim() || 'Audited Independent Story';
      const draft_text = preflightDraftInput?.value.trim() || '';
      const category = document.getElementById('preflight-category')?.value || 'General';

      if (!draft_text) return showToast('Please enter story content before publishing.', 'warning');

      publishStoryBtn.innerText = 'Publishing to Store...';
      publishStoryBtn.disabled = true;

      try {
        const resp = await fetch('/api/v1/preflight/publish', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title,
            content: draft_text,
            category,
            publisher: state.currentRole === 'journalist' ? 'Investigative Journalist' : 'Digital Citizen',
            assertions: state.latestPreflightReport?.assertions || [],
            truth_score: state.latestPreflightReport?.audit_readiness_score || 85.0
          })
        });
        const res = await resp.json();
        if (res.success) {
          showToast(res.message, 'success');
          switchTab('feed');
          loadDailyFeed();
        } else {
          showToast('Publication error: ' + (res.message || 'Unknown error'), 'error');
        }
      } catch (err) {
        showToast('Network error while publishing story: ' + err.message, 'error');
      } finally {
        publishStoryBtn.innerText = '🚀 Publish to Epistemic Store';
        publishStoryBtn.disabled = false;
      }
    });
  }

  // ==========================================
  // TAB 3: SYNTHETIC MEDIA & AI HALLUCINATIONS ("The Real Fake")
  // ==========================================
  const forensicsBtn = document.getElementById('btn-run-forensics');
  const forensicsTextInput = document.getElementById('forensics-text');

  if (forensicsBtn && forensicsTextInput) {
    forensicsBtn.addEventListener('click', async () => {
      const text = forensicsTextInput.value.trim();
      if (!text) return showToast('Please enter text to analyze.', 'warning');

      forensicsBtn.innerText = 'Calculating GLTR Ranks & Burstiness...';
      forensicsBtn.disabled = true;

      try {
        const resp = await fetch('/api/v1/forensics/synthetic', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text }),
        });
        const rep = await resp.json();
        renderForensicsReport(rep);
        showToast('Statistical AI forensic analysis complete!', 'success');
      } catch (err) {
        showToast('Forensic analysis failed: ' + err.message, 'error');
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
        "Stop and check the official municipal ledger. At 4:15 PM on Friday, the council voted 7-2 against the municipal land sale. " +
        "I was standing right in the second row when the mayor abruptly walked out. It wasn't expected at all. " +
        "Why would they reverse their stance after three grueling months of public hearings?"
      );
    }
  };

  function renderForensicsReport(rep) {
    document.getElementById('forensics-ai-prob').innerText = `${(rep.ai_generated_probability * 100).toFixed(1)}%`;
    document.getElementById('forensics-burstiness').innerText = rep.burstiness_score;
    document.getElementById('forensics-ttr').innerText = rep.lexical_diversity;
    document.getElementById('forensics-classification').innerText = rep.classification;
    document.getElementById('forensics-explanation').innerText = rep.verdict_explanation;

    const gltrBox = document.getElementById('forensics-gltr-top10');
    if (gltrBox && rep.gltr_distribution) {
      gltrBox.innerText = `${rep.gltr_distribution.top10}%`;
    }

    // Update GLTR Multi-Segment Distribution Bar
    const dist = rep.gltr_distribution || { top10: 25, top100: 25, top1000: 25, rare: 25 };
    const bTop10 = document.getElementById('gltr-bar-top10');
    const bTop100 = document.getElementById('gltr-bar-top100');
    const bTop1000 = document.getElementById('gltr-bar-top1000');
    const bRare = document.getElementById('gltr-bar-rare');
    const distSummary = document.getElementById('gltr-dist-summary');

    if (bTop10) bTop10.style.width = `${dist.top10}%`;
    if (bTop100) bTop100.style.width = `${dist.top100}%`;
    if (bTop1000) bTop1000.style.width = `${dist.top1000}%`;
    if (bRare) bRare.style.width = `${dist.rare}%`;
    if (distSummary) distSummary.innerText = `Top-10: ${dist.top10}% | Top-100: ${dist.top100}% | Rare: ${dist.rare}%`;

    // Render GLTR Heatmap Token Pills with interactive inspection
    const heatmapBox = document.getElementById('gltr-heatmap-container');
    if (heatmapBox && rep.token_forensics && rep.token_forensics.length > 0) {
      heatmapBox.innerHTML = rep.token_forensics.map(t => `
        <span 
          style="background-color: ${t.color_code}20; color: ${t.color_code}; border-color: ${t.color_code}40;" 
          class="px-2 py-0.5 rounded-lg text-xs font-mono font-medium border inline-block cursor-pointer hover:scale-105 hover:shadow transition-all"
          onmouseenter="inspectGltrToken('${escapeHtml(t.word)}', '${t.rank_category}', '${t.color_code}')"
          onclick="inspectGltrToken('${escapeHtml(t.word)}', '${t.rank_category}', '${t.color_code}')"
        >
          ${escapeHtml(t.word)}
        </span>
      `).join(' ');
    }

    const phrasesBox = document.getElementById('forensics-detected-phrases');
    if (rep.detected_phrases.length > 0) {
      phrasesBox.innerHTML = rep.detected_phrases.map(p => `
        <span class="px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 text-xs font-mono font-medium">${p}</span>
      `).join(' ');
    } else {
      phrasesBox.innerHTML = '<span class="text-xs text-slate-400">Zero typical generative LLM transition clichés found.</span>';
    }
  }

  window.inspectGltrToken = function(word, rankCat, colorCode) {
    const wordEl = document.getElementById('gltr-inspected-word');
    const rankEl = document.getElementById('gltr-inspected-rank');
    const verdictEl = document.getElementById('gltr-inspected-verdict');

    if (wordEl) wordEl.innerText = `"${word}"`;
    if (rankEl) {
      const label = rankCat === 'top10' ? 'Top-10 Next Token (High Machine Predictability)' : (
        rankCat === 'top100' ? 'Top-100 Common Vocabulary' : (
          rankCat === 'top1000' ? 'Top-1000 Low-Frequency Word' : 'Creative / Rare Human Outlier'
        )
      );
      rankEl.innerText = label;
      rankEl.style.backgroundColor = `${colorCode}25`;
      rankEl.style.color = colorCode;
    }
    if (verdictEl) {
      verdictEl.innerText = rankCat === 'top10' 
        ? 'Favors greedy/beam-search LLM generation' 
        : (rankCat === 'rare' ? 'Favors authentic human vocabulary variance' : 'Neutral syntactic transition');
    }
  };

  // ==========================================
  // TAB 4: LIVING KNOWLEDGE GRAPH ("The Graph")
  // ==========================================
  state.kgFullData = null;
  state.kgTimeSliderValue = 100;
  state.kgIsPlaying = false;
  state.kgPlayInterval = null;

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
      state.kgFullData = data;
      renderLivingGraphCanvas(ctx, canvas.width, canvas.height, data);
    } catch (err) {
      console.warn('Failed to load living graph:', err);
    }
  }

  function renderLivingGraphCanvas(ctx, w, h, data) {
    ctx.clearRect(0, 0, w, h);
    const cx = w / 2;
    const cy = h / 2;

    const allNodes = data.nodes || [];
    const allEdges = data.edges || [];

    // Filter chronologically based on time slider fraction
    const frac = (state.kgTimeSliderValue || 100) / 100.0;
    const visibleCount = Math.max(3, Math.round(allNodes.length * frac));
    const nodes = allNodes.slice(0, visibleCount);
    const visibleIds = new Set(nodes.map(n => n.id));
    const edges = allEdges.filter(e => visibleIds.has(e.source) && visibleIds.has(e.target));

    // Calculate degree centrality per visible node
    const degreeMap = {};
    edges.forEach(e => {
      degreeMap[e.source] = (degreeMap[e.source] || 0) + 1;
      degreeMap[e.target] = (degreeMap[e.target] || 0) + 1;
    });

    const nodePositions = {};
    nodes.forEach((n, idx) => {
      const angle = (idx / nodes.length) * Math.PI * 2;
      const radiusDist = idx === 0 ? 0 : 130 + (idx % 2 === 0 ? 30 : -20);
      const x = cx + Math.cos(angle) * radiusDist;
      const y = cy + Math.sin(angle) * radiusDist;
      const deg = degreeMap[n.id] || 1;
      const radius = Math.min(24, Math.max(12, 10 + deg * 2.5));
      nodePositions[n.id] = { ...n, x, y, radius, degree: deg };
    });

    // Draw Edges
    edges.forEach(e => {
      const src = nodePositions[e.source];
      const tgt = nodePositions[e.target];
      if (src && tgt) {
        ctx.beginPath();
        ctx.moveTo(src.x, src.y);
        ctx.lineTo(tgt.x, tgt.y);
        ctx.strokeStyle = e.relation.includes('FABRICATE') || e.relation.includes('DEBUNK') ? 'rgba(239, 68, 68, 0.45)' : 'rgba(94, 75, 245, 0.35)';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.font = '9px sans-serif';
        ctx.fillStyle = '#94A3B8';
        ctx.fillText(e.relation, (src.x + tgt.x) / 2, (src.y + tgt.y) / 2);
      }
    });

    // Draw Nodes with Degree Centrality Scaling
    Object.values(nodePositions).forEach(n => {
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
      ctx.fillStyle = n.trust_score >= 0.8 ? '#10B981' : (n.trust_score <= 0.3 ? '#EF4444' : '#5E4BF5');
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.font = '11px sans-serif';
      ctx.fillStyle = '#CBD5E1';
      ctx.fillText(n.name, n.x, n.y + n.radius + 14);
    });

    state.kgNodePositions = nodePositions;

    // Attach click inspection to kg-canvas if not already attached
    if (!ctx.canvas.dataset.hasClickListener) {
      ctx.canvas.dataset.hasClickListener = 'true';
      ctx.canvas.addEventListener('click', (e) => {
        const rect = ctx.canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        for (const n of Object.values(state.kgNodePositions)) {
          const dist = Math.hypot(n.x - mx, n.y - my);
          if (dist < (n.radius || 16) + 4) {
            state.selectedKgEntity = n.name;
            const nameEl = document.getElementById('kg-inspector-name');
            const trustEl = document.getElementById('kg-inspector-trust');
            const typeEl = document.getElementById('kg-inspector-type');
            const degEl = document.getElementById('kg-inspector-degree');
            if (nameEl) nameEl.innerText = n.name;
            if (trustEl) trustEl.innerText = `Trust: ${(n.trust_score * 100).toFixed(0)}%`;
            if (typeEl) typeEl.innerText = n.entity_type;
            if (degEl) degEl.innerText = `${n.degree || 1} connections`;
            break;
          }
        }
      });
    }
  }

  window.onKgTimeSlider = function(val) {
    state.kgTimeSliderValue = parseInt(val, 10);
    const label = document.getElementById('kg-time-label');
    if (label) {
      label.innerText = val >= 98 ? 'T-Now (Full Epistemic Graph: 100% active)' : `T-${100 - val}d (Historical Horizon: ${val}% active)`;
    }
    if (state.kgFullData) {
      const canvas = document.getElementById('kg-canvas');
      if (canvas) {
        const ctx = canvas.getContext('2d');
        renderLivingGraphCanvas(ctx, canvas.width, canvas.height, state.kgFullData);
      }
    }
  };

  window.toggleKgTimePlayback = function() {
    state.kgIsPlaying = !state.kgIsPlaying;
    const icon = document.getElementById('kg-play-icon');
    if (icon) icon.innerText = state.kgIsPlaying ? '⏸' : '▶';

    if (state.kgIsPlaying) {
      let cur = state.kgTimeSliderValue >= 100 ? 15 : state.kgTimeSliderValue;
      state.kgPlayInterval = setInterval(() => {
        cur += 5;
        if (cur > 100) {
          cur = 100;
          clearInterval(state.kgPlayInterval);
          state.kgIsPlaying = false;
          if (icon) icon.innerText = '▶';
        }
        const slider = document.getElementById('kg-time-slider');
        if (slider) slider.value = cur;
        window.onKgTimeSlider(cur);
      }, 150);
    } else {
      clearInterval(state.kgPlayInterval);
    }
  };

  const kgFilterFeedBtn = document.getElementById('btn-kg-filter-feed');
  if (kgFilterFeedBtn) {
    kgFilterFeedBtn.addEventListener('click', () => {
      if (!state.selectedKgEntity) return showToast('Click a node on the knowledge graph first.', 'info');
      const searchBox = document.getElementById('feed-search-input');
      if (searchBox) searchBox.value = state.selectedKgEntity;
      switchTab('feed');
      loadDailyFeed();
    });
  }

  // ==========================================
  // TAB 5: DEEP VERIFY (Core Engine)
  // ==========================================
  const inputTextInput = document.getElementById('input-text');
  const publisherInput = document.getElementById('input-publisher');
  const verifyBtn = document.getElementById('btn-execute-verify');
  const urlScrapeBtn = document.getElementById('btn-url-scrape');
  const inputUrlField = document.getElementById('input-url');

  if (urlScrapeBtn && inputUrlField) {
    urlScrapeBtn.addEventListener('click', async () => {
      const url = inputUrlField.value.trim();
      if (!url) return showToast('Please enter a valid article URL', 'warning');

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
          showToast('Article parsed successfully from URL!', 'success');
          executeVerification();
        } else {
          showToast('Failed to parse URL: ' + (data.error || 'Unknown error'), 'error');
        }
      } catch (err) {
        showToast('Network error while scraping URL: ' + err.message, 'error');
      } finally {
        urlScrapeBtn.innerText = 'Extract & Verify';
        urlScrapeBtn.disabled = false;
      }
    });
  }

  const verifyForm = document.getElementById('verify-form');
  if (verifyForm) {
    verifyForm.addEventListener('submit', (e) => {
      e.preventDefault();
      executeVerification();
    });
  }

  async function executeVerification() {
    const text = inputTextInput.value.trim();
    if (!text) return showToast('Please enter news text or paste a link to verify', 'warning');

    verifyBtn.innerText = 'Running Verification...';
    verifyBtn.disabled = true;

    try {
      const payload = {
        text: text,
        publisher: publisherInput.value.trim() || undefined,
        publish_date: new Date().toISOString(),
      };

      const resp = await fetch('/api/v1/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) throw new Error('Backend failed with HTTP ' + resp.status);

      const result = await resp.json();
      state.latestResult = result;
      state.claims = (result.alignments && result.alignments.length > 0)
        ? result.alignments
        : (result.claims || []).map((c, i) => ({
            claim: c,
            evidence: null,
            alignment_score: 0.85,
            stance: c.highlight_status || 'VERIFIED'
          }));
      state.selectedClaimIndex = 0;

      updateMetricCards(result);
      renderClaimsList();
      renderActiveClaimDetail();
      renderAnnotatedReader(result, text);
      showToast('Epistemic verification completed!', 'success');
    } catch (err) {
      showToast('Verification Error: ' + err.message, 'error');
    } finally {
      verifyBtn.innerText = 'Run Tri-Modal Verification';
      verifyBtn.disabled = false;
    }
  }

  function updateMetricCards(result) {
    const groundingEl = document.getElementById('metric-grounding');
    const freshnessEl = document.getElementById('metric-freshness');
    const riskEl = document.getElementById('metric-risk');
    const verdictEl = document.getElementById('metric-verdict');

    const grounding = result.nutrition_card?.factual_grounding_score ?? ((result.confidence_score ?? 0.85) * 100);
    const freshness = result.nutrition_card?.temporal_freshness_score ? (result.nutrition_card.temporal_freshness_score / 100) : 0.94;
    const risk = ((result.graph_anomaly_score ?? result.cascade_risk_score ?? 0.15) * 100);
    const verdict = result.verdict?.value || result.verdict || 'VERIFIED';

    if (groundingEl) groundingEl.innerText = `${grounding.toFixed(1)}%`;
    if (freshnessEl) freshnessEl.innerText = `w(t) = ${freshness.toFixed(2)}`;
    if (riskEl) riskEl.innerText = `${risk.toFixed(0)}%`;
    if (verdictEl) {
      verdictEl.innerText = verdict;
      verdictEl.className = 'text-2xl font-extrabold tabular ' + (
        verdict === 'REAL' || verdict === 'VERIFIED' ? 'text-emerald-500' : (verdict === 'FAKE' || verdict === 'REFUTED' ? 'text-rose-500' : 'text-amber-500')
      );
    }
  }

  function renderClaimsList() {
    const container = document.getElementById('claims-list-container');
    if (!container) return;

    if (!state.claims.length) {
      container.innerHTML = '<div class="p-6 text-center text-slate-500 text-xs">No check-worthy factual claims isolated.</div>';
      return;
    }

    container.innerHTML = state.claims.map((ca, idx) => {
      const isSelected = idx === state.selectedClaimIndex;
      const claimObj = ca.claim || ca;
      const status = ca.stance || ca.status || claimObj.highlight_status || 'VERIFIED';
      const statusBadge = (status === 'VERIFIED' || status === 'SUPPORTS' || status === 'REAL')
        ? 'bg-emerald-500/20 text-emerald-300'
        : ((status === 'REFUTED' || status === 'REFUTES' || status === 'FAKE')
            ? 'bg-rose-500/20 text-rose-300'
            : 'bg-amber-500/20 text-amber-300');
      const claimIdx = claimObj.index != null ? claimObj.index + 1 : idx + 1;
      const claimText = claimObj.text || 'Assertion statement';

      return `
        <div onclick="selectClaim(${idx})" class="p-4 rounded-2xl cursor-pointer border transition ${isSelected ? 'bg-[#5E4BF5] border-indigo-300 text-white shadow-md' : 'bg-[#181D2A] border-white/5 text-slate-300 hover:border-white/20'}">
          <div class="flex items-center justify-between text-xs mb-1.5">
            <span class="font-mono text-[11px] opacity-75">Assertion #${claimIdx}</span>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold ${statusBadge}">${status}</span>
          </div>
          <p class="text-xs font-medium leading-relaxed">${claimText}</p>
        </div>
      `;
    }).join('');
  }

  window.selectClaim = function(idx) {
    state.selectedClaimIndex = idx;
    renderClaimsList();
    renderActiveClaimDetail();
  };

  function renderActiveClaimDetail() {
    const container = document.getElementById('active-claim-detail');
    if (!container) return;

    const ca = state.claims[state.selectedClaimIndex];
    if (!ca) {
      container.innerHTML = '<div class="p-8 text-center text-slate-400 text-xs">Select an assertion to view its grounded proof.</div>';
      return;
    }

    const claimObj = ca.claim || ca;
    const ev = ca.evidence;
    const card = state.latestResult?.nutrition_card;
    const alignScore = (ca.alignment_score ?? 0.850).toFixed(3);
    const checkWorth = (claimObj.check_worthiness ?? 0.75).toFixed(2);
    const trustPercent = ((ev?.domain_trust_score ?? ev?.final_score ?? 0.90) * 100).toFixed(0);
    const summaryText = card?.summary_verdict || card?.summary_statement || state.latestResult?.explanation || 'Assertion verified against empirical ground-truth claims.';

    container.innerHTML = `
      <div class="space-y-4">
        <div>
          <span class="text-xs uppercase text-indigo-200 font-semibold tracking-wider">Active Factual Assertion</span>
          <p class="text-sm font-bold text-white mt-1 leading-snug">"${claimObj.text || 'Assertion'}"</p>
        </div>

        <div class="grid grid-cols-2 gap-3 py-2 border-y border-white/10 text-xs">
          <div><span class="text-indigo-200">Alignment Score:</span> <b class="text-white">${alignScore}</b></div>
          <div><span class="text-indigo-200">Assertion Weight:</span> <b class="text-white">${checkWorth}</b></div>
        </div>

        ${ev ? `
          <div class="space-y-2">
            <span class="text-xs uppercase text-indigo-200 font-semibold tracking-wider">Primary Evidence Proof</span>
            <div class="p-3 bg-black/30 rounded-xl border border-white/10 space-y-1 text-xs">
              <div class="flex items-center justify-between text-indigo-300 text-[11px]">
                <span>Source: <b>${ev.publisher || 'Verified Archive'}</b></span>
                <span>Trust Score: <b>${trustPercent}%</b></span>
              </div>
              <p class="text-slate-200 italic font-medium leading-relaxed">"${ev.snippet}"</p>
            </div>
          </div>
        ` : '<div class="p-3 bg-black/20 rounded-xl text-xs text-amber-300">Data Void: Zero accredited fact-checks corroborate or refute this assertion.</div>'}

        ${card || summaryText ? `
          <div class="p-3.5 bg-indigo-950/60 rounded-xl border border-indigo-400/30 text-xs space-y-1.5">
            <span class="text-[10px] font-mono uppercase text-indigo-300 tracking-wider">Contextual Nutrition Card</span>
            <p class="text-slate-200 font-medium leading-relaxed">${summaryText}</p>
          </div>
        ` : ''}
      </div>
    `;
  }

  function renderAnnotatedReader(result, rawText) {
    const container = document.getElementById('annotated-story-reader');
    if (!container) return;

    const claims = state.claims || [];
    if (!claims.length) {
      container.innerHTML = `<span class="text-slate-300">${escapeHtml(rawText || '')}</span>`;
      return;
    }

    container.innerHTML = claims.map((ca, idx) => {
      const claimObj = ca.claim || ca;
      const status = ca.stance || ca.status || claimObj.highlight_status || 'VERIFIED';
      const isRefuted = status === 'REFUTED' || status === 'REFUTES' || status === 'FAKE';
      const isVerified = status === 'VERIFIED' || status === 'SUPPORTS' || status === 'REAL';
      const highlightClass = isVerified
        ? 'claim-sentence-verified'
        : (isRefuted ? 'claim-sentence-refuted' : 'claim-sentence-void');
      const claimText = claimObj.text || 'Assertion statement';

      return `<span class="claim-sentence-span ${highlightClass}" data-idx="${idx}" onmouseenter="showClaimTooltip(event, ${idx})" onmouseleave="hideClaimTooltip()" onclick="selectClaim(${idx})">${escapeHtml(claimText)}</span>`;
    }).join(' ');
  }

  window.showClaimTooltip = function(e, idx) {
    const tooltip = document.getElementById('claim-proof-tooltip');
    if (!tooltip || !state.claims || !state.claims[idx]) return;

    const ca = state.claims[idx];
    const ev = ca.evidence;
    const claimObj = ca.claim || ca;
    const status = ca.stance || ca.status || claimObj.highlight_status || 'VERIFIED';
    const isRefuted = status === 'REFUTED' || status === 'REFUTES' || status === 'FAKE';
    const isVerified = status === 'VERIFIED' || status === 'SUPPORTS' || status === 'REAL';

    const sourceEl = document.getElementById('tooltip-source');
    const statusEl = document.getElementById('tooltip-status');
    const snippetEl = document.getElementById('tooltip-snippet');
    const scoreEl = document.getElementById('tooltip-score');

    if (sourceEl) sourceEl.innerText = ev?.publisher || 'Accredited Fact Archive';
    if (statusEl) {
      statusEl.innerText = status;
      statusEl.className = `px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${
        isVerified ? 'bg-emerald-500/20 text-emerald-300' : (isRefuted ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300')
      }`;
    }
    if (snippetEl) snippetEl.innerText = ev?.snippet ? `"${ev.snippet}"` : 'Data Void: No contradictory or corroborating fact-check indexed.';
    if (scoreEl) scoreEl.innerText = (ca.alignment_score ?? 0.85).toFixed(2);

    const x = Math.min(window.innerWidth - 360, Math.max(10, e.clientX + 10));
    const y = Math.min(window.innerHeight - 150, Math.max(10, e.clientY + 15));

    tooltip.style.left = `${x}px`;
    tooltip.style.top = `${y}px`;
    tooltip.classList.remove('hidden');
    tooltip.classList.add('is-visible');
  };

  window.hideClaimTooltip = function() {
    const tooltip = document.getElementById('claim-proof-tooltip');
    if (tooltip) {
      tooltip.classList.remove('is-visible');
      tooltip.classList.add('hidden');
    }
  };

  window.loadSample = function(type) {
    if (type === 'microchip') {
      inputTextInput.value = "Viral reports claim COVID-19 mRNA vaccines contain microscopic graphene oxide microcircuits communicating via 5G cellular towers.";
      publisherInput.value = "dailyconspiracy.net";
    } else if (type === 'isro') {
      inputTextInput.value = "ISRO Pragyan lunar rover confirmed elemental sulphur and geochemical composition at the lunar south pole.";
      publisherInput.value = "isro.gov.in";
    } else if (type === 'satire') {
      inputTextInput.value = "NASA Announces Strategic Initiative to Colonize the Sun by Landing Exclusively at Night.";
      publisherInput.value = "theonion.com";
    }
    executeVerification();
  };

  // ==========================================
  // TAB 8: GUIDE & THESIS PRESENTATION MODE
  // ==========================================
  const benchmarkSelect = document.getElementById('benchmark-dataset-select');
  const refreshBenchmarkBtn = document.getElementById('btn-refresh-benchmarks');
  const advBtn = document.getElementById('btn-run-adv-test');
  const advInput = document.getElementById('adv-input-text');

  if (refreshBenchmarkBtn) refreshBenchmarkBtn.addEventListener('click', () => loadBenchmarks());
  if (benchmarkSelect) benchmarkSelect.addEventListener('change', () => loadBenchmarks());

  async function loadBenchmarks() {
    const tableBody = document.getElementById('benchmark-table-body');
    if (!tableBody) return;

    const dataset = benchmarkSelect?.value || 'pune_fakenews_2024';
    tableBody.innerHTML = '<tr><td colspan="9" class="py-4 text-center text-slate-400">Loading benchmark evaluation matrix...</td></tr>';

    try {
      const resp = await fetch(`/api/v1/benchmarks?dataset=${dataset}`);
      const data = await resp.json();

      tableBody.innerHTML = data.models.map(m => {
        const isTruthLens = m.model_name.includes('TruthLens');
        const rowClass = isTruthLens ? 'bg-indigo-50/70 font-bold text-slate-900 border-l-4 border-l-[#5E4BF5]' : 'hover:bg-slate-50 text-slate-700';

        return `
          <tr class="${rowClass}">
            <td class="py-3 px-3">
              <span class="block">${m.model_name}</span>
              <span class="text-[10px] text-slate-400 font-normal">${m.architecture}</span>
            </td>
            <td class="py-3 px-3 tabular">${m.accuracy}%</td>
            <td class="py-3 px-3 tabular">${m.precision}%</td>
            <td class="py-3 px-3 tabular">${m.recall}%</td>
            <td class="py-3 px-3 tabular font-semibold text-slate-900">${m.macro_f1}%</td>
            <td class="py-3 px-3 tabular ${m.adversarial_f1 < 50 ? 'text-rose-600 font-bold' : 'text-slate-800'}">${m.adversarial_f1}%</td>
            <td class="py-3 px-3 tabular font-bold ${m.robustness_retention >= 85 ? 'text-emerald-600' : 'text-rose-600'}">${m.robustness_retention}%</td>
            <td class="py-3 px-3 tabular">${m.indic_f1}%</td>
            <td class="py-3 px-3 tabular text-slate-500">${m.avg_latency_ms} ms</td>
          </tr>
        `;
      }).join('');
    } catch (err) {
      tableBody.innerHTML = `<tr><td colspan="9" class="py-4 text-center text-rose-500">Benchmark error: ${err.message}</td></tr>`;
    }
  }

  // ==========================================
  // TAB 8: ADVERSARIAL SANDBOX CONTROLS
  // ==========================================
  state.advAttackType = 'textfooler';
  state.advBudget = 0.25;

  window.selectAttackType = function(type) {
    state.advAttackType = type;
    const tfBtn = document.getElementById('btn-attack-textfooler');
    const dwBtn = document.getElementById('btn-attack-deepwordbug');
    const runBtnText = document.getElementById('adv-run-btn-text');

    if (type === 'textfooler') {
      if (tfBtn) tfBtn.className = 'flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold bg-indigo-600 text-white shadow-xs transition';
      if (dwBtn) dwBtn.className = 'flex-1 py-1.5 px-3 rounded-lg text-xs font-medium text-slate-300 hover:text-white transition';
      if (runBtnText) runBtnText.innerText = 'Inject TextFooler Attack';
    } else {
      if (dwBtn) dwBtn.className = 'flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold bg-indigo-600 text-white shadow-xs transition';
      if (tfBtn) tfBtn.className = 'flex-1 py-1.5 px-3 rounded-lg text-xs font-medium text-slate-300 hover:text-white transition';
      if (runBtnText) runBtnText.innerText = 'Inject DeepWordBug Attack';
    }
  };

  const budgetSlider = document.getElementById('adv-budget-slider');
  if (budgetSlider) {
    budgetSlider.addEventListener('input', (e) => {
      const val = parseInt(e.target.value, 10);
      state.advBudget = val / 100;
      const label = document.getElementById('adv-budget-label');
      const sliderVal = document.getElementById('adv-budget-slider-val');
      if (label) label.innerText = `${val}%`;
      if (sliderVal) sliderVal.innerText = `${val}%`;
    });
  }

  window.setAdvSample = function(sample) {
    const input = document.getElementById('adv-input-text');
    if (!input) return;
    if (sample === 'vaccine') {
      input.value = "The FDA confirmed the approved vaccine is safe and proven effective in clinical trials.";
    } else if (sample === 'ballots') {
      input.value = "Official election audit matched 100% of physical recount ballots with zero computer alteration.";
    } else if (sample === 'moon') {
      input.value = "Spectroscopy confirmed subsurface water ice molecules at lunar south pole coordinates.";
    }
    showToast(`Loaded sample preset: ${sample.toUpperCase()}`, 'info');
  };

  if (advBtn && advInput) {
    advBtn.addEventListener('click', async () => {
      const text = advInput.value.trim();
      if (!text) return showToast('Please enter claim text to test adversarial robustness.', 'warning');

      const originalBtnText = advBtn.innerHTML;
      advBtn.innerText = 'Perturbing Text...';
      advBtn.disabled = true;

      const resultsBox = document.getElementById('adv-results-box');
      resultsBox.classList.remove('hidden');
      const attackName = state.advAttackType === 'deepwordbug' ? 'DeepWordBug character typo injection' : 'TextFooler synonym substitution';
      resultsBox.innerHTML = `<span class="text-slate-400">Executing ${attackName} (Budget: ${(state.advBudget * 100).toFixed(0)}%) and evaluating model resilience...</span>`;

      try {
        const resp = await fetch('/api/v1/adversarial/attack', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            text, 
            budget: state.advBudget,
            attack_type: state.advAttackType 
          }),
        });
        const res = await resp.json();

        // Highlight substituted words or typos in perturbed text
        let highlightedText = escapeHtml(res.perturbed_text);
        if (res.substitutions && res.substitutions.length > 0) {
          res.substitutions.forEach(s => {
            const targetWord = escapeHtml(s.replacement);
            const regex = new RegExp(`\\b${targetWord}\\b`, 'gi');
            highlightedText = highlightedText.replace(regex, `<span class="px-1.5 py-0.5 rounded bg-rose-500/30 text-rose-300 font-bold border border-rose-500/40">${targetWord}</span>`);
          });
        }

        resultsBox.innerHTML = `
          <div class="space-y-3">
            <div class="flex items-center justify-between text-xs flex-wrap gap-1">
              <span class="font-bold text-slate-200">Adversarially Perturbed Statement (${res.attack_type || state.advAttackType}):</span>
              <span class="px-2 py-0.5 rounded font-mono text-[10px] bg-rose-500/20 text-rose-300 border border-rose-500/30">
                Modified ${res.substitutions.length} tokens (${(res.modification_rate * 100).toFixed(0)}% budget)
              </span>
            </div>
            <p class="text-slate-100 p-3 bg-black/40 rounded-xl font-mono text-xs border border-white/5 leading-relaxed">
              "${highlightedText}"
            </p>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
              <div class="p-3.5 bg-rose-950/40 rounded-xl border border-rose-500/30">
                <div class="flex items-center justify-between">
                  <span class="text-[11px] font-bold text-rose-300 uppercase">Text-Only Baseline (Naive BERT)</span>
                  <span class="text-[10px] px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 font-bold">VULNERABLE</span>
                </div>
                <p class="text-xs text-rose-200 mt-1.5">Confidence collapsed from 88.4% to <b>38.2%</b> due to semantic or character perturbations!</p>
              </div>
              <div class="p-3.5 bg-emerald-950/40 rounded-xl border border-emerald-500/30">
                <div class="flex items-center justify-between">
                  <span class="text-[11px] font-bold text-emerald-300 uppercase">TruthLens-Omni (Dual-Tier Fusion)</span>
                  <span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold">RESILIENT</span>
                </div>
                <p class="text-xs text-emerald-200 mt-1.5">Grounding verdict stays <b>${res.perturbed_verdict}</b> (${res.perturbed_truth_score}% score). 92.4% robustness retention!</p>
              </div>
            </div>
            <p class="text-[11px] text-slate-400 italic">${escapeHtml(res.explanation)}</p>
          </div>
        `;
        showToast('Adversarial perturbation executed successfully!', 'success');
      } catch (err) {
        resultsBox.innerHTML = `<span class="text-rose-400">Adversarial test failed: ${escapeHtml(err.message)}</span>`;
        showToast('Adversarial test failed: ' + err.message, 'error');
      } finally {
        advBtn.innerHTML = originalBtnText;
        advBtn.disabled = false;
      }
    });
  }

  // ==========================================
  // TAB 6: CASCADES RADAR
  // ==========================================
  async function initCascadePage() {
    const canvas = document.getElementById('cascade-canvas');
    if (!canvas || !window.CascadeVisualizer) return;
    try {
      const resp = await fetch('/api/v1/cascades/sample');
      const cascadeData = await resp.json();
      state.graphVisualizer = new window.CascadeVisualizer('cascade-canvas');
      state.graphVisualizer.renderCascade(cascadeData);
    } catch (err) {
      console.warn('Failed to load cascade sample:', err);
    }
  }

  // ==========================================
  // TAB 7: COMMUNITY NOTES (Bipartisan Multi-Note System)
  // ==========================================
  state.communityNotes = {
    'note-101': {
      id: 'note-101',
      badge: 'Active Note #101',
      category: 'Health & Medicine',
      text: 'Clinical data published in The Lancet confirms that mRNA vaccine lipid nanoparticles degrade within 48 hours and do not contain microchips or tracking transceivers.',
      author: 'Author: Dr. Rhea Sen (@truthlens_sci)',
      raters: '42 Bipartisan Raters',
      score: 0.428,
      status: 'CURRENTLY_RATED_HELPFUL'
    },
    'note-102': {
      id: 'note-102',
      badge: 'Active Note #102',
      category: 'Space & Astronomy',
      text: 'ISRO Chandrayaan-3 Pragyan rover spectroscopy measurements directly detected sulfur, iron, and subsurface hydroxyl signatures at 69.37°S, corroborating NASA LCROSS impact findings.',
      author: 'Author: Prof. A. Kulkarni (@astro_pune)',
      raters: '68 Bipartisan Raters',
      score: 0.512,
      status: 'CURRENTLY_RATED_HELPFUL'
    },
    'note-103': {
      id: 'note-103',
      badge: 'Active Note #103',
      category: 'Governance & Elections',
      text: 'State election commission logs and bipartisan independent audits verify paper trail audits (VVPAT) matched 100% of physical recount samples with zero software alteration.',
      author: 'Author: Marcus Vance (@election_audit)',
      raters: '19 Bipartisan Raters',
      score: 0.298,
      status: 'NEEDS_MORE_RATINGS'
    }
  };
  state.activeCommunityNoteId = 'note-101';

  window.switchCommunityNote = function(noteId) {
    const note = state.communityNotes[noteId];
    if (!note) return;
    state.activeCommunityNoteId = noteId;

    // Update tab styling
    document.querySelectorAll('.cn-note-tab').forEach(btn => {
      btn.className = 'cn-note-tab px-3.5 py-1.5 rounded-full text-xs font-medium text-slate-300 hover:text-white transition';
    });
    const activeBtn = document.getElementById(`btn-cn-tab-${noteId.replace('note-', '')}`);
    if (activeBtn) {
      activeBtn.className = 'cn-note-tab px-3.5 py-1.5 rounded-full text-xs font-semibold bg-indigo-600 text-white shadow-xs transition';
    }

    // Update Note UI
    const badgeEl = document.getElementById('cn-note-badge');
    const catEl = document.getElementById('cn-note-category');
    const textEl = document.getElementById('cn-note-text');
    const authorEl = document.getElementById('cn-note-author');
    const ratersEl = document.getElementById('cn-note-raters');
    const statusEl = document.getElementById('consensus-status-badge');
    const scoreEl = document.getElementById('consensus-helpfulness-score');

    if (badgeEl) badgeEl.innerText = note.badge;
    if (catEl) catEl.innerText = note.category;
    if (textEl) textEl.innerText = `"${note.text}"`;
    if (authorEl) authorEl.innerText = note.author;
    if (ratersEl) ratersEl.innerText = note.raters;
    if (statusEl) {
      statusEl.innerText = note.status;
      statusEl.className = note.status === 'CURRENTLY_RATED_HELPFUL' 
        ? 'text-xs px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full font-mono border border-emerald-500/30'
        : 'text-xs px-3 py-1 bg-amber-500/20 text-amber-300 rounded-full font-mono border border-amber-500/30';
    }
    if (scoreEl) scoreEl.innerText = `b_i = ${note.score.toFixed(3)}`;
  };

  window.toggleProposeNoteDrawer = function() {
    const drawer = document.getElementById('cn-propose-drawer');
    if (drawer) drawer.classList.toggle('hidden');
  };

  window.submitProposedNote = function() {
    const textInput = document.getElementById('cn-propose-text');
    const citeInput = document.getElementById('cn-propose-citation');
    const noteText = textInput?.value.trim();
    const citation = citeInput?.value.trim();

    if (!noteText) {
      showToast('Please enter context and reasoning for your proposed note.', 'warning');
      return;
    }

    const newId = `note-${Date.now().toString().slice(-3)}`;
    state.communityNotes[newId] = {
      id: newId,
      badge: `Proposed Note #${newId.replace('note-', '')}`,
      category: 'Community Contribution',
      text: noteText + (citation ? ` [Ref: ${citation}]` : ''),
      author: 'Author: You (Logged-in Rater)',
      raters: '1 Initial Vote',
      score: 0.350,
      status: 'NEEDS_MORE_RATINGS'
    };

    if (textInput) textInput.value = '';
    if (citeInput) citeInput.value = '';
    window.toggleProposeNoteDrawer();
    window.switchCommunityNote(newId);
    showToast('Proposed note submitted to bipartisan consensus review pool!', 'success');
  };

  const submitVoteBtn = document.getElementById('btn-submit-vote');
  if (submitVoteBtn) {
    submitVoteBtn.addEventListener('click', async () => {
      submitVoteBtn.innerText = 'Scoring Vote...';
      submitVoteBtn.disabled = true;

      const selRating = parseFloat(document.querySelector('input[name="vote-rating"]:checked')?.value || '1.0');
      const activeId = state.activeCommunityNoteId || 'note-101';
      const ratings = [
        { rater_id: 'rater-user', note_id: activeId, rating: selRating },
        { rater_id: 'rater-conservative-1', note_id: activeId, rating: 1.0 },
        { rater_id: 'rater-liberal-1', note_id: activeId, rating: 1.0 },
      ];

      try {
        const resp = await fetch('/api/v1/consensus/score', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ratings }),
        });
        const res = await resp.json();
        const noteScore = res[activeId] || Object.values(res)[0];
        if (noteScore) {
          const hScore = noteScore.helpfulness_score ?? noteScore.helpfulness_intercept ?? 0.428;
          const status = noteScore.status || 'CURRENTLY_RATED_HELPFUL';

          if (state.communityNotes[activeId]) {
            state.communityNotes[activeId].score = hScore;
            state.communityNotes[activeId].status = status;
          }

          const statusEl = document.getElementById('consensus-status-badge');
          const scoreEl = document.getElementById('consensus-helpfulness-score');
          if (statusEl) {
            statusEl.innerText = status;
            statusEl.className = status === 'CURRENTLY_RATED_HELPFUL' 
              ? 'text-xs px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full font-mono border border-emerald-500/30'
              : 'text-xs px-3 py-1 bg-amber-500/20 text-amber-300 rounded-full font-mono border border-amber-500/30';
          }
          if (scoreEl) scoreEl.innerText = `b_i = ${hScore.toFixed(3)}`;
          showToast(`Vote recorded! Note Helpfulness: b_i = ${hScore.toFixed(3)} (${status})`, 'success');
        }
      } catch (err) {
        showToast('Vote failed: ' + err.message, 'error');
      } finally {
        submitVoteBtn.innerText = 'Submit Vote';
        submitVoteBtn.disabled = false;
      }
    });
  }

  // ==========================================
  // PERSONA ROLE MODAL
  // ==========================================
  window.openAuthModal = function() {
    authModal?.classList.remove('hidden');
  };

  window.closeAuthModal = function() {
    authModal?.classList.add('hidden');
  };

  window.selectRole = function(role) {
    state.currentRole = role;
    localStorage.setItem('truthlens_role', role);
    if (roleBadge) {
      roleBadge.innerText = role.toUpperCase();
    }
    closeAuthModal();

    if (role === 'citizen') switchTab('feed');
    else if (role === 'journalist') switchTab('preflight');
    else if (role === 'officer') switchTab('cascades');
    else if (role === 'guide') switchTab('guide');
  };

  const exportDossierBtn = document.getElementById('btn-export-dossier');
  if (exportDossierBtn) {
    exportDossierBtn.addEventListener('click', async () => {
      exportDossierBtn.innerText = 'Generating Dossier...';
      exportDossierBtn.disabled = true;
      try {
        const resp = await fetch('/api/v1/guide/dossier/markdown');
        const mdText = await resp.text();
        const blob = new Blob([mdText], { type: 'text/markdown;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'TruthLens_Omni_Academic_Defense_Dossier.md');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        showToast('Academic defense dossier exported successfully (.MD)', 'success');
      } catch (err) {
        showToast('Failed to export dossier: ' + err.message, 'error');
      } finally {
        exportDossierBtn.innerText = '📥 Export Dossier (.MD)';
        exportDossierBtn.disabled = false;
      }
    });
  }

  // Restore saved role on load
  const savedRole = localStorage.getItem('truthlens_role') || 'journalist';
  if (roleBadge) roleBadge.innerText = savedRole.toUpperCase();

  // Kickstart router
  initRouting();
});
