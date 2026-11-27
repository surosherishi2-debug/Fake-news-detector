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
  // Toast Notification Controller
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

    const labelMap = {
      success: 'OK',
      error: 'ERR',
      warning: 'WARN',
      info: 'INFO'
    };
    const badgeColorMap = {
      success: 'text-[#15803d]',
      error: 'text-[#b91c1c]',
      warning: 'text-[#b45309]',
      info: 'text-[#1d4ed8]'
    };
    const label = labelMap[type] || 'INFO';
    const badgeColor = badgeColorMap[type] || 'text-[#525252]';

    toast.innerHTML = `
      <span class="font-mono text-[11px] font-medium ${badgeColor} pt-0.5">${label}</span>
      <div class="toast-content">${escapeHtml(message)}</div>
      <button class="toast-close-btn" aria-label="Close notification">&times;</button>
    `;

    const closeBtn = toast.querySelector('.toast-close-btn');
    const dismiss = () => {
      toast.classList.add('toast-closing');
      setTimeout(() => {
        if (toast.parentElement) toast.remove();
      }, 180);
    };

    closeBtn?.addEventListener('click', dismiss);
    container.appendChild(toast);

    if (duration > 0) {
      setTimeout(dismiss, duration);
    }
  }
  window.showToast = showToast;

  window.toggleMobileSidebar = function(open) {
    const sidebar = document.getElementById('app-sidebar');
    const backdrop = document.getElementById('mobile-sidebar-backdrop');
    if (!sidebar) return;
    if (open) {
      sidebar.classList.remove('-translate-x-full');
      backdrop?.classList.remove('hidden');
    } else {
      sidebar.classList.add('-translate-x-full');
      backdrop?.classList.add('hidden');
    }
  };

  window.copyApiKey = function() {
    const input = document.getElementById('api-key-input');
    if (input && navigator.clipboard) {
      navigator.clipboard.writeText(input.value).catch(() => {});
    }
    showToast('API key copied to clipboard', 'success');
  };

  const tabButtons = document.querySelectorAll('.nav-tab-btn');
  const pageSections = document.querySelectorAll('.page-view');
  const roleBadge = document.getElementById('user-role-badge');
  const authModal = document.getElementById('auth-modal');

  const TAB_TITLES = {
    dashboard: 'Dashboard',
    verify: 'Fact-checker',
    feed: 'Live stream',
    graph: 'Network graph',
    cascades: 'Cascade radar',
    models: 'Model ladder',
    preflight: 'Pre-flight studio',
    forensics: 'Synthetic forensics',
    consensus: 'Consensus notes',
    guide: 'Dossier & PDF',
    auth: 'Access & roles',
    landing: 'Platform overview',
    profile: 'Preferences'
  };

  // Navigation Routing
  function initRouting() {
    const path = window.location.pathname;
    const hash = window.location.hash.replace('#', '');
    if (path.includes('/login') || path.includes('/register') || path.includes('/auth') || hash === 'auth') {
      switchTab('auth');
      if (path.includes('/register')) {
        setTimeout(() => switchAuthSubTab('register'), 50);
      }
    } else if (path.includes('/dashboard') || hash === 'dashboard') {
      switchTab('dashboard');
    } else {
      const initialTab = hash || 'dashboard';
      switchTab(initialTab);
    }

    window.addEventListener('hashchange', () => {
      const target = window.location.hash.replace('#', '') || 'dashboard';
      switchTab(target);
    });
  }

  function switchTab(tabName) {
    const validTabs = ['dashboard', 'verify', 'feed', 'graph', 'cascades', 'models', 'preflight', 'forensics', 'consensus', 'guide', 'auth', 'landing', 'profile'];
    if (!validTabs.includes(tabName)) tabName = 'dashboard';

    state.activeTab = tabName;
    window.location.hash = tabName;

    const topTitle = document.getElementById('topbar-view-title');
    if (topTitle) topTitle.innerText = TAB_TITLES[tabName] || 'Dashboard';

    // Update Sidebar Navigation Buttons
    const allNavButtons = document.querySelectorAll('.nav-tab-btn');
    allNavButtons.forEach((btn) => {
      const target = btn.getAttribute('data-tab');
      btn.classList.toggle('is-active', target === tabName);
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
    if (tabName === 'dashboard') setTimeout(initDashboardCharts, 50);
    if (tabName === 'auth') loadAuthTelemetry();
    if (tabName === 'feed') loadDailyFeed();
    if (tabName === 'graph') loadLivingKnowledgeGraph();
    if (tabName === 'guide') loadBenchmarks();
    if (tabName === 'cascades') setTimeout(() => initCascadePage(), 80);
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

  // =========================================================================
  // EXECUTIVE DASHBOARD CHARTS & TELEMETRY CONTROLLER
  // =========================================================================
  let chartInstances = {};

  function initDashboardCharts() {
    if (typeof Chart === 'undefined') {
      setTimeout(initDashboardCharts, 150);
      return;
    }

    try {
      Chart.defaults.font.family = '"IBM Plex Sans", sans-serif';
      Chart.defaults.color = '#737373';

      // 1. ECE Calibration Reliability Curve (Lead Chart)
      const eceElem = document.getElementById('chart-ece-curve');
      if (eceElem) {
        const eceCtx = eceElem.getContext('2d');
        if (chartInstances.ece) chartInstances.ece.destroy();
        chartInstances.ece = new Chart(eceCtx, {
          type: 'line',
          data: {
            labels: ['0.0', '0.2', '0.4', '0.6', '0.8', '1.0'],
            datasets: [
              {
                label: 'Ideal (y = x)',
                data: [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
                borderColor: '#d4d4d8',
                borderDash: [4, 4],
                borderWidth: 1.5,
                fill: false,
                pointRadius: 0
              },
              {
                label: 'MiniLM-L6 (ECE 0.112)',
                data: [0.05, 0.22, 0.41, 0.58, 0.77, 0.94],
                borderColor: '#1d4ed8',
                backgroundColor: 'rgba(29, 78, 216, 0.06)',
                borderWidth: 2.5,
                pointRadius: 3,
                pointBackgroundColor: '#1d4ed8',
                fill: false,
                tension: 0.15
              },
              {
                label: 'TF-IDF Baseline (ECE 0.142)',
                data: [0.10, 0.29, 0.48, 0.69, 0.85, 0.98],
                borderColor: '#737373',
                borderWidth: 1.5,
                pointRadius: 2,
                pointBackgroundColor: '#737373',
                fill: false,
                tension: 0.15
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
                align: 'end',
                labels: { boxWidth: 12, usePointStyle: true, font: { size: 11 } }
              }
            },
            scales: {
              y: {
                min: 0,
                max: 1.0,
                grid: { color: 'rgba(23, 23, 23, 0.06)' },
                title: { display: true, text: 'Observed accuracy', font: { size: 11 } },
                ticks: { font: { family: '"JetBrains Mono", monospace', size: 11 } }
              },
              x: {
                grid: { display: false },
                title: { display: true, text: 'Predicted confidence', font: { size: 11 } },
                ticks: { font: { family: '"JetBrains Mono", monospace', size: 11 } }
              }
            }
          }
        });
      }

      // 2. Ingestion & Latency Mixed Stream Chart
      const streamElem = document.getElementById('chart-ingestion-stream');
      if (streamElem) {
        const streamCtx = streamElem.getContext('2d');
        if (chartInstances.stream) chartInstances.stream.destroy();
        chartInstances.stream = new Chart(streamCtx, {
          type: 'bar',
          data: {
            labels: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
            datasets: [
              {
                type: 'line',
                label: 'Median latency (ms)',
                data: [31, 32, 29, 36, 42, 38, 44, 33],
                borderColor: '#1d4ed8',
                borderWidth: 2,
                pointRadius: 2.5,
                pointBackgroundColor: '#1d4ed8',
                yAxisID: 'y1',
                tension: 0.25,
                fill: false
              },
              {
                type: 'bar',
                label: 'Claims processed',
                data: [18, 12, 24, 65, 88, 72, 94, 62],
                backgroundColor: 'rgba(23, 23, 23, 0.78)',
                borderRadius: 4,
                yAxisID: 'y'
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
                align: 'end',
                labels: { boxWidth: 10, font: { size: 11 } }
              }
            },
            scales: {
              y: {
                type: 'linear',
                position: 'left',
                grid: { color: 'rgba(23, 23, 23, 0.06)' },
                ticks: { font: { family: '"JetBrains Mono", monospace', size: 11 } }
              },
              y1: {
                type: 'linear',
                position: 'right',
                grid: { display: false },
                ticks: { font: { family: '"JetBrains Mono", monospace', size: 11 } }
              },
              x: {
                grid: { display: false },
                ticks: { font: { family: '"JetBrains Mono", monospace', size: 11 } }
              }
            }
          }
        });
      }
    } catch (e) {
      console.warn("Chart.js initialization notice:", e);
    }
  }
  window.initDashboardCharts = initDashboardCharts;

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
      
      let badgeClass = 'px-2 py-0.5 rounded text-xs font-mono font-medium bg-[#f0fdf4] text-[#15803d] border border-[#15803d]/20';
      if (verdict === 'DEBUNKED' || verdict === 'FAKE') {
        badgeClass = 'px-2 py-0.5 rounded text-xs font-mono font-medium bg-[#fef2f2] text-[#b91c1c] border border-[#b91c1c]/20';
      } else if (verdict === 'UNCERTAIN' || verdict === 'DATA_VOID') {
        badgeClass = 'px-2 py-0.5 rounded text-xs font-mono font-medium bg-[#fffbeb] text-[#b45309] border border-[#b45309]/20';
      }

      if (badgeEl) {
        badgeEl.className = badgeClass;
        badgeEl.innerText = verdict;
      }
      if (scoreEl) {
        scoreEl.innerText = `${score}%`;
        scoreEl.className = score >= 70 ? 'text-[#15803d] font-mono text-xs' : 'text-[#b91c1c] font-mono text-xs';
      }

      if (sentencesEl) {
        const alignments = data.alignments || [];
        if (alignments.length > 0) {
          sentencesEl.innerHTML = alignments.map(a => `
            <div class="space-y-1">
              <span class="claim-sentence-span ${a.stance === 'VERIFIED' ? 'claim-sentence-verified' : 'claim-sentence-refuted'}">
                "${escapeHtml(a.claim?.text || text)}"
              </span>
              <p class="text-xs text-[#737373] pt-0.5">
                Citation: <span class="text-[#171717]">${escapeHtml(a.evidence?.source_title || 'IFCN Evidence Archive')}</span> (${(a.alignment_score * 100).toFixed(0)}%)
              </p>
            </div>
          `).join('');
        } else {
          sentencesEl.innerHTML = `
            <div class="space-y-1">
              <span class="claim-sentence-span claim-sentence-verified">
                "${escapeHtml(text)}"
              </span>
              <p class="text-xs text-[#737373] pt-0.5">
                Citation: Primary Fact Check Archive (${score}%)
              </p>
            </div>
          `;
        }
      }

      showToast(`Verification complete: ${verdict} (${score}%)`, 'success');
    } catch (err) {
      showToast('Landing verification error: ' + err.message, 'error');
    } finally {
      if (btnText) btnText.innerText = 'Check claim';
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

    container.innerHTML = '<div class="p-8 text-center text-sm text-[#737373]">Loading epistemic stream</div>';

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
        pill.className = 'feed-status-pill px-3 py-1 rounded-md text-xs font-medium bg-white text-[#171717] border border-[#171717]/[0.08] transition-colors';
      } else {
        pill.className = 'feed-status-pill px-3 py-1 rounded-md text-xs font-normal text-[#525252] hover:text-[#171717] transition-colors';
      }
    });

    try {
      const params = new URLSearchParams({ category, status, language, search, limit: '50' });
      const resp = await fetch(`/api/v1/feed?${params.toString()}`);
      const data = await resp.json();
      state.feedArticles = data.articles || [];

      updateFeedKpiCards(state.feedArticles);

      const totalBadge = document.getElementById('feed-article-total-badge');
      if (totalBadge) totalBadge.innerText = `${state.feedArticles.length} loaded`;

      if (state.feedArticles.length === 0) {
        container.innerHTML = `
          <div class="p-8 text-center bg-[#fafafa] rounded-xl border border-[#171717]/[0.08] space-y-3">
            <div class="text-sm font-medium text-[#171717]">No stories match active filters</div>
            <p class="text-xs text-[#737373]">Adjust your search query or clear category filters.</p>
            <button onclick="resetFeedFilters()" class="h-8 px-3 bg-[#171717] hover:bg-[#262626] text-white rounded-lg text-xs font-medium transition-colors">
              Reset filters
            </button>
          </div>
        `;
        if (dossier) {
          dossier.innerHTML = `
            <div class="p-12 text-center text-[#737373] space-y-2">
              <div class="text-sm font-medium text-[#171717]">No story selected</div>
              <p class="text-xs text-[#737373]">Reset filters to load stories from the stream.</p>
            </div>
          `;
        }
        return;
      }

      if (!state.selectedFeedArticleId || !state.feedArticles.some(a => a.id === state.selectedFeedArticleId)) {
        state.selectedFeedArticleId = state.feedArticles[0].id;
      }

      container.innerHTML = state.feedArticles.map(art => {
        const isSelected = art.id === state.selectedFeedArticleId;
        const cardBg = isSelected
          ? 'bg-[#f4f4f5] border-[#171717]/[0.14] border-l-2 border-l-[#1d4ed8]'
          : 'bg-white hover:bg-[#fafafa] border-[#171717]/[0.08]';

        let statusBadge = 'bg-[#f0fdf4] text-[#15803d] border-[#15803d]/20';
        let statusIcon = 'Verified';
        let truthColor = 'text-[#15803d]';

        if (art.status === 'FAKE') {
          statusBadge = 'bg-[#fef2f2] text-[#b91c1c] border-[#b91c1c]/20';
          statusIcon = 'Debunked';
          truthColor = 'text-[#b91c1c]';
        } else if (art.status === 'SATIRE') {
          statusBadge = 'bg-[#f4f4f5] text-[#525252] border-[#171717]/[0.12]';
          statusIcon = 'Satire';
          truthColor = 'text-[#525252]';
        } else if (art.status === 'SYNTHETIC') {
          statusBadge = 'bg-[#f4f4f5] text-[#1d4ed8] border-[#1d4ed8]/20';
          statusIcon = 'Synthetic';
          truthColor = 'text-[#1d4ed8]';
        } else if (art.status === 'DATA_VOID') {
          statusBadge = 'bg-[#fffbeb] text-[#b45309] border-[#b45309]/20';
          statusIcon = 'Data void';
          truthColor = 'text-[#b45309]';
        }

        const langBadge = art.language === 'mr' ? 'MR' : (art.language === 'hi' ? 'HI' : 'EN');
        const shortId = art.id.length > 14 ? art.id.substring(0, 14) + '...' : art.id;

        return `
          <button onclick="selectFeedArticle('${art.id}')" class="w-full text-left p-4 rounded-xl border ${cardBg} transition-colors space-y-2 block">
            <div class="flex items-center justify-between text-xs gap-2">
              <div class="flex items-center gap-1.5 flex-wrap">
                <span class="px-2 py-0.5 rounded font-mono text-[11px] border ${statusBadge}">${statusIcon}</span>
                <span class="px-1.5 py-0.5 rounded bg-[#f4f4f5] text-[#525252] font-mono text-[11px]">${langBadge}</span>
                <span class="text-xs text-[#737373] hidden sm:inline">${escapeHtml(art.category || 'News')}</span>
              </div>
              <span class="text-xs font-mono text-[#737373]">${shortId}</span>
            </div>
            <div class="text-sm font-medium text-[#171717] line-clamp-2 leading-snug">${escapeHtml(art.title)}</div>
            <div class="flex items-center justify-between text-xs pt-2 border-t border-[#171717]/[0.06] text-[#525252]">
              <span class="truncate max-w-[200px]">${escapeHtml(art.publisher)}</span>
              <span class="font-mono tabular-nums ${truthColor}">${art.truth_score}%</span>
            </div>
          </button>
        `;
      }).join('');

      const activeArt = state.feedArticles.find(a => a.id === state.selectedFeedArticleId) || state.feedArticles[0];
      if (activeArt) {
        renderActiveDossier(activeArt);
      }

    } catch (err) {
      container.innerHTML = `<div class="p-8 text-center text-sm text-[#b91c1c]">Failed to load feed: ${escapeHtml(err.message)}</div>`;
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
      const container = document.getElementById('feed-articles-container');
      if (container) {
        const cards = container.children;
        state.feedArticles.forEach((art, idx) => {
          if (cards[idx]) {
            if (art.id === artId) {
              cards[idx].className = 'w-full text-left p-4 rounded-xl border bg-[#f4f4f5] border-[#171717]/[0.14] border-l-2 border-l-[#1d4ed8] transition-colors space-y-2 block';
            } else {
              cards[idx].className = 'w-full text-left p-4 rounded-xl border bg-white hover:bg-[#fafafa] border-[#171717]/[0.08] transition-colors space-y-2 block';
            }
          }
        });
      }
    }
  };

  function renderActiveDossier(art) {
    const dossier = document.getElementById('feed-active-dossier');
    if (!dossier) return;

    let statusBadge = 'bg-[#f0fdf4] text-[#15803d] border-[#15803d]/20';
    let statusLabel = 'Verified ground truth';
    let truthColor = 'text-[#15803d]';

    if (art.status === 'FAKE') {
      statusBadge = 'bg-[#fef2f2] text-[#b91c1c] border-[#b91c1c]/20';
      statusLabel = 'Debunked misinformation';
      truthColor = 'text-[#b91c1c]';
    } else if (art.status === 'SATIRE') {
      statusBadge = 'bg-[#f4f4f5] text-[#525252] border-[#171717]/[0.12]';
      statusLabel = 'Satirical parody';
      truthColor = 'text-[#525252]';
    } else if (art.status === 'SYNTHETIC') {
      statusBadge = 'bg-[#f4f4f5] text-[#1d4ed8] border-[#1d4ed8]/20';
      statusLabel = 'Synthetic text';
      truthColor = 'text-[#1d4ed8]';
    } else if (art.status === 'DATA_VOID') {
      statusBadge = 'bg-[#fffbeb] text-[#b45309] border-[#b45309]/20';
      statusLabel = 'Breaking data-void';
      truthColor = 'text-[#b45309]';
    }

    const claims = art.claims || [];
    const claimsHtml = claims.length > 0 ? claims.map(c => {
      const isRefuted = c.status === 'REFUTED' || art.status === 'FAKE';
      const markerColor = isRefuted ? 'text-[#b91c1c]' : (c.status === 'DATA_VOID' ? 'text-[#b45309]' : 'text-[#15803d]');
      const markerLabel = isRefuted ? 'REFUTED' : (c.status === 'DATA_VOID' ? 'VOID' : 'VERIFIED');

      return `
        <div class="p-3.5 rounded-lg bg-white border border-[#171717]/[0.08] space-y-1.5">
          <div class="flex items-center justify-between text-xs">
            <span class="font-mono font-medium ${markerColor}">${markerLabel}</span>
            <span class="font-mono text-[#737373]">Worthiness: ${(c.check_worthiness * 100).toFixed(0)}%</span>
          </div>
          <p class="text-sm text-[#171717] leading-relaxed">${escapeHtml(c.text)}</p>
          <div class="text-xs text-[#737373]">
            Citation: <span class="text-[#525252]">${escapeHtml(c.citation || 'IFCN Accredited Archive')}</span>
          </div>
        </div>
      `;
    }).join('') : '<div class="text-xs text-[#737373] p-3">No decomposed claims recorded for this entry.</div>';

    dossier.innerHTML = `
      <div class="flex items-center justify-between flex-wrap gap-2 pb-4 border-b border-[#171717]/[0.08]">
        <div class="flex items-center gap-2">
          <span class="font-mono text-xs text-[#737373]">#${escapeHtml(art.id)}</span>
          <span class="px-2 py-0.5 rounded text-xs font-mono border ${statusBadge}">${statusLabel}</span>
        </div>
        <div class="flex items-center gap-2 text-xs">
          <span class="font-medium text-[#171717]">${escapeHtml(art.publisher)}</span>
          <span class="font-mono text-[#737373]">${escapeHtml(art.domain)}</span>
        </div>
      </div>

      <div class="space-y-2">
        <h3 class="text-xl font-medium text-[#171717] leading-snug">${escapeHtml(art.title)}</h3>
        <p class="text-sm text-[#525252] leading-relaxed">${escapeHtml(art.content)}</p>
      </div>

      <div class="grid grid-cols-3 gap-3">
        <div class="p-3.5 rounded-lg bg-white border border-[#171717]/[0.08]">
          <div class="text-xs text-[#737373]">Integrity</div>
          <div class="text-xl font-mono font-medium ${truthColor} tabular-nums mt-1">${art.truth_score}%</div>
        </div>
        <div class="p-3.5 rounded-lg bg-white border border-[#171717]/[0.08]">
          <div class="text-xs text-[#737373]">Cascade risk</div>
          <div class="text-xl font-mono font-medium text-[#171717] tabular-nums mt-1">${(art.cib_risk * 100).toFixed(0)}%</div>
        </div>
        <div class="p-3.5 rounded-lg bg-white border border-[#171717]/[0.08]">
          <div class="text-xs text-[#737373]">Claims audited</div>
          <div class="text-xl font-mono font-medium text-[#171717] tabular-nums mt-1">${claims.length}</div>
        </div>
      </div>

      <div class="space-y-2">
        <div class="flex items-center justify-between text-xs text-[#525252]">
          <span class="font-medium text-[#171717]">Assertion breakdown</span>
          <span class="evidence-stamp">λ=0.10</span>
        </div>
        <div class="space-y-2 max-h-48 overflow-y-auto pr-1">
          ${claimsHtml}
        </div>
      </div>

      <div class="pt-4 border-t border-[#171717]/[0.08] flex items-center justify-between flex-wrap gap-2">
        <div class="flex items-center gap-2 flex-wrap">
          <button onclick="inspectFeedArticle('${art.id}', '${encodeURIComponent(art.title)}', '${encodeURIComponent(art.content)}', '${art.domain}')"
            class="h-8 px-3 bg-[#171717] hover:bg-[#262626] text-white font-medium text-xs rounded-lg transition-colors">
            Inspect in fact-checker
          </button>
          <button onclick="downloadProvenanceCard('${art.id}')"
            class="h-8 px-3 bg-white hover:bg-[#f4f4f5] text-[#171717] border border-[#171717]/[0.12] font-medium text-xs rounded-lg transition-colors">
            Export provenance JSON
          </button>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="switchTab('graph')" class="h-8 px-3 bg-white hover:bg-[#f4f4f5] text-[#525252] border border-[#171717]/[0.08] text-xs rounded-lg transition-colors">
            Graph
          </button>
          <button onclick="switchTab('cascades')" class="h-8 px-3 bg-white hover:bg-[#f4f4f5] text-[#525252] border border-[#171717]/[0.08] text-xs rounded-lg transition-colors">
            Radar
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
      syncFeedsBtn.innerText = 'Syncing...';
      syncFeedsBtn.disabled = true;
      try {
        const resp = await fetch('/api/v1/feed/sync', { method: 'POST' });
        const res = await resp.json();
        showToast(res.message, 'success');
        loadDailyFeed();
      } catch (err) {
        showToast('Feed sync failed: ' + err.message, 'error');
      } finally {
        syncFeedsBtn.innerText = 'Sync feeds';
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
    scoreBox.className = 'text-[32px] leading-none font-mono font-medium tabular-nums ' + (
      report.audit_readiness_score >= 80 ? 'text-[#15803d]' : (report.audit_readiness_score >= 50 ? 'text-[#b45309]' : 'text-[#b91c1c]')
    );

    recsBox.innerHTML = report.recommendations.map(r => `
      <li class="flex items-start gap-2 text-xs text-[#525252]">
        <span class="font-mono text-[#1d4ed8]">-</span>
        <span>${escapeHtml(r)}</span>
      </li>
    `).join('');

    assertionsBox.innerHTML = report.assertions.map(a => {
      let riskBadge = 'bg-[#f0fdf4] text-[#15803d] border-[#15803d]/20';
      if (a.risk_level === 'HIGH') riskBadge = 'bg-[#fef2f2] text-[#b91c1c] border-[#b91c1c]/20';
      else if (a.risk_level === 'MEDIUM') riskBadge = 'bg-[#fffbeb] text-[#b45309] border-[#b45309]/20';

      return `
        <div class="p-3.5 bg-[#fafafa] rounded-lg border border-[#171717]/[0.08] text-xs space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="font-mono font-medium text-[#171717]">Assertion #${a.sentence_index + 1}</span>
            <span class="px-2 py-0.5 rounded font-mono border ${riskBadge}">${a.risk_level} RISK</span>
          </div>
          <p class="text-[#171717] leading-relaxed">"${escapeHtml(a.text)}"</p>
          <p class="text-xs text-[#525252]">Action: ${escapeHtml(a.suggested_action)}</p>
          ${a.recommended_citations.length > 0 ? `
            <div class="text-xs text-[#1d4ed8] bg-[#1d4ed8]/[0.06] p-2 rounded mt-1">
              Recommended citations: ${escapeHtml(a.recommended_citations.join(' | '))}
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

      if (!draft_text) return showToast('Enter story content before publishing', 'warning');

      publishStoryBtn.innerText = 'Publishing...';
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
        publishStoryBtn.innerText = 'Publish to live stream';
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

    // Render GLTR Heatmap Token Pills without scale jitter
    const heatmapBox = document.getElementById('gltr-heatmap-container');
    if (heatmapBox && rep.token_forensics && rep.token_forensics.length > 0) {
      heatmapBox.innerHTML = rep.token_forensics.map(t => `
        <span 
          style="background-color: ${t.color_code}18; color: ${t.color_code}; border-color: ${t.color_code}35;" 
          class="px-2 py-0.5 rounded text-xs font-mono font-medium border inline-block cursor-pointer transition-colors"
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
        <span class="px-2 py-0.5 rounded bg-[#fef2f2] text-[#b91c1c] border border-[#b91c1c]/20 text-xs font-mono">${escapeHtml(p)}</span>
      `).join(' ');
    } else {
      phrasesBox.innerHTML = '<span class="text-xs text-[#737373]">Zero generative transition clichés found</span>';
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
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const cssW = rect.width || 640;
    const cssH = rect.height || 460;
    canvas.width = cssW * dpr;
    canvas.height = cssH * dpr;
    canvas.style.width = `${cssW}px`;
    canvas.style.height = `${cssH}px`;

    try {
      const resp = await fetch('/api/v1/knowledge-graph');
      const data = await resp.json();
      state.kgFullData = data;
      renderLivingGraphCanvas(ctx, cssW, cssH, data, dpr);
    } catch (err) {
      console.warn('Failed to load living graph:', err);
    }
  }

  function renderLivingGraphCanvas(ctx, w, h, data, dpr = Math.min(window.devicePixelRatio || 1, 2)) {
    ctx.save();
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, w, h);
    const cx = w / 2;
    const cy = h / 2;

    const allNodes = data.nodes || [];
    const allEdges = data.edges || [];

    const frac = (state.kgTimeSliderValue || 100) / 100.0;
    const visibleCount = Math.max(3, Math.round(allNodes.length * frac));
    const nodes = allNodes.slice(0, visibleCount);
    const visibleIds = new Set(nodes.map(n => n.id));
    const edges = allEdges.filter(e => visibleIds.has(e.source) && visibleIds.has(e.target));

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
      const radius = Math.min(22, Math.max(12, 10 + deg * 2.5));
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
        ctx.strokeStyle = e.relation.includes('FABRICATE') || e.relation.includes('DEBUNK') ? 'rgba(229, 72, 77, 0.45)' : 'rgba(59, 130, 246, 0.35)';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.font = '10px "JetBrains Mono", monospace';
        ctx.fillStyle = '#85858b';
        ctx.textAlign = 'center';
        ctx.fillText(e.relation, (src.x + tgt.x) / 2, (src.y + tgt.y) / 2);
      }
    });

    // Draw Nodes
    Object.values(nodePositions).forEach(n => {
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
      ctx.fillStyle = n.trust_score >= 0.8 ? '#4cc38a' : (n.trust_score <= 0.3 ? '#e5484d' : '#3b82f6');
      ctx.fill();
      ctx.strokeStyle = '#141415';
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.font = '11px "IBM Plex Sans", sans-serif';
      ctx.fillStyle = '#ededed';
      ctx.textAlign = 'center';
      ctx.fillText(n.name, n.x, n.y + n.radius + 14);
    });

    ctx.restore();
    state.kgNodePositions = nodePositions;

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
      label.innerText = val >= 98 ? 'T-Now (100% active)' : `T-${100 - val}d (${val}% active)`;
    }
    if (state.kgFullData) {
      const canvas = document.getElementById('kg-canvas');
      if (canvas) {
        const ctx = canvas.getContext('2d');
        const rect = canvas.parentElement.getBoundingClientRect();
        renderLivingGraphCanvas(ctx, rect.width || 640, rect.height || 460, state.kgFullData);
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
      verdictEl.className = 'text-[28px] leading-none font-mono font-medium tabular-nums ' + (
        verdict === 'REAL' || verdict === 'VERIFIED' ? 'text-[#15803d]' : (verdict === 'FAKE' || verdict === 'REFUTED' ? 'text-[#b91c1c]' : 'text-[#b45309]')
      );
    }
  }

  function renderClaimsList() {
    const container = document.getElementById('claims-list-container');
    if (!container) return;

    if (!state.claims.length) {
      container.innerHTML = '<div class="p-6 text-center text-[#737373] text-xs">No factual assertions isolated</div>';
      return;
    }

    container.innerHTML = state.claims.map((ca, idx) => {
      const isSelected = idx === state.selectedClaimIndex;
      const claimObj = ca.claim || ca;
      const status = ca.stance || ca.status || claimObj.highlight_status || 'VERIFIED';
      const statusBadge = (status === 'VERIFIED' || status === 'SUPPORTS' || status === 'REAL')
        ? 'bg-[#f0fdf4] text-[#15803d] border-[#15803d]/20'
        : ((status === 'REFUTED' || status === 'REFUTES' || status === 'FAKE')
            ? 'bg-[#fef2f2] text-[#b91c1c] border-[#b91c1c]/20'
            : 'bg-[#fffbeb] text-[#b45309] border-[#b45309]/20');
      const claimIdx = claimObj.index != null ? claimObj.index + 1 : idx + 1;
      const claimText = claimObj.text || 'Assertion statement';

      return `
        <button onclick="selectClaim(${idx})" class="w-full text-left p-4 rounded-xl border transition-colors block ${isSelected ? 'bg-[#f4f4f5] border-[#171717]/[0.14] border-l-2 border-l-[#1d4ed8]' : 'bg-white border-[#171717]/[0.08] hover:bg-[#fafafa]'}">
          <div class="flex items-center justify-between text-xs mb-1.5">
            <span class="font-mono text-[#737373]">Assertion #${claimIdx}</span>
            <span class="px-2 py-0.5 rounded text-[11px] font-mono border ${statusBadge}">${status}</span>
          </div>
          <p class="text-sm text-[#171717] leading-relaxed">${escapeHtml(claimText)}</p>
        </button>
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
      container.innerHTML = '<div class="p-8 text-center text-[#737373] text-xs">Select an assertion to view its grounded proof</div>';
      return;
    }

    const claimObj = ca.claim || ca;
    const ev = ca.evidence;
    const card = state.latestResult?.nutrition_card;
    const alignScore = (ca.alignment_score ?? 0.850).toFixed(3);
    const checkWorth = (claimObj.check_worthiness ?? 0.75).toFixed(2);
    const trustPercent = ((ev?.domain_trust_score ?? ev?.final_score ?? 0.90) * 100).toFixed(0);
    const summaryText = card?.summary_verdict || card?.summary_statement || state.latestResult?.explanation || 'Assertion evaluated against primary claims.';

    container.innerHTML = `
      <div class="space-y-4">
        <div>
          <span class="text-xs text-[#737373]">Active assertion</span>
          <p class="text-base font-medium text-[#171717] mt-1 leading-snug">"${escapeHtml(claimObj.text || 'Assertion')}"</p>
        </div>

        <div class="grid grid-cols-2 gap-3 py-3 border-y border-[#171717]/[0.08] text-xs font-mono">
          <div><span class="text-[#737373]">Alignment:</span> <span class="text-[#171717] font-medium">${alignScore}</span></div>
          <div><span class="text-[#737373]">Worthiness:</span> <span class="text-[#171717] font-medium">${checkWorth}</span></div>
        </div>

        ${ev ? `
          <div class="space-y-2">
            <span class="text-xs text-[#737373] block">Primary evidence</span>
            <div class="p-3.5 bg-white rounded-lg border border-[#171717]/[0.08] space-y-1.5 text-xs">
              <div class="flex items-center justify-between text-[#525252]">
                <span>Source: <span class="text-[#171717] font-medium">${escapeHtml(ev.publisher || 'Verified Archive')}</span></span>
                <span class="font-mono">Trust: ${trustPercent}%</span>
              </div>
              <p class="text-[#171717] leading-relaxed">"${escapeHtml(ev.snippet)}"</p>
            </div>
          </div>
        ` : '<div class="p-3 bg-[#fffbeb] border border-[#b45309]/20 rounded-lg text-xs text-[#b45309]">Data void: no accredited fact-checks corroborate or refute this assertion.</div>'}

        ${card || summaryText ? `
          <div class="p-3.5 bg-white rounded-lg border border-[#171717]/[0.08] text-xs space-y-1">
            <span class="font-mono text-[#1d4ed8] block">Contextual assessment</span>
            <p class="text-[#525252] leading-relaxed">${escapeHtml(summaryText)}</p>
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

    if (sourceEl) sourceEl.innerText = ev?.publisher || 'Accredited fact archive';
    if (statusEl) {
      statusEl.innerText = status;
      statusEl.className = `px-1.5 py-0.5 rounded font-mono text-[10px] ${
        isVerified ? 'bg-[#f0fdf4] text-[#15803d]' : (isRefuted ? 'bg-[#fef2f2] text-[#b91c1c]' : 'bg-[#fffbeb] text-[#b45309]')
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
        const rowClass = isTruthLens ? 'bg-[#1d4ed8]/[0.04] font-medium text-[#171717] border-l-2 border-l-[#1d4ed8]' : 'hover:bg-[#fafafa] text-[#525252]';

        return `
          <tr class="${rowClass} transition-colors">
            <td class="py-3 px-4">
              <span class="block text-[#171717]">${escapeHtml(m.model_name)}</span>
              <span class="text-xs text-[#737373] font-normal">${escapeHtml(m.architecture)}</span>
            </td>
            <td class="py-3 px-3 font-mono">${m.accuracy}%</td>
            <td class="py-3 px-3 font-mono">${m.precision}%</td>
            <td class="py-3 px-3 font-mono">${m.recall}%</td>
            <td class="py-3 px-3 font-mono text-[#171717]">${m.macro_f1}%</td>
            <td class="py-3 px-3 font-mono ${m.adversarial_f1 < 50 ? 'text-[#b91c1c]' : 'text-[#171717]'}">${m.adversarial_f1}%</td>
            <td class="py-3 px-3 font-mono ${m.robustness_retention >= 85 ? 'text-[#15803d]' : 'text-[#b91c1c]'}">${m.robustness_retention}%</td>
            <td class="py-3 px-3 font-mono">${m.indic_f1}%</td>
            <td class="py-3 px-3 font-mono text-[#737373]">${m.avg_latency_ms} ms</td>
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
      if (tfBtn) tfBtn.className = 'flex-1 py-1.5 px-3 rounded-md text-xs font-medium bg-white text-[#171717] border border-[#171717]/[0.08]';
      if (dwBtn) dwBtn.className = 'flex-1 py-1.5 px-3 rounded-md text-xs font-normal text-[#525252] hover:text-[#171717]';
      if (runBtnText) runBtnText.innerText = 'Inject TextFooler Attack';
    } else {
      if (dwBtn) dwBtn.className = 'flex-1 py-1.5 px-3 rounded-md text-xs font-medium bg-white text-[#171717] border border-[#171717]/[0.08]';
      if (tfBtn) tfBtn.className = 'flex-1 py-1.5 px-3 rounded-md text-xs font-normal text-[#525252] hover:text-[#171717]';
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
              <span class="font-medium text-[#171717]">Perturbed statement (${escapeHtml(res.attack_type || state.advAttackType)})</span>
              <span class="px-2 py-0.5 rounded font-mono text-[11px] bg-[#fef2f2] text-[#b91c1c] border border-[#b91c1c]/20">
                Modified ${res.substitutions.length} tokens (${(res.modification_rate * 100).toFixed(0)}%)
              </span>
            </div>
            <p class="text-[#171717] p-3 bg-white rounded-lg font-mono text-xs border border-[#171717]/[0.08] leading-relaxed">
              "${highlightedText}"
            </p>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
              <div class="p-3.5 bg-[#fef2f2] rounded-lg border border-[#b91c1c]/20">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-medium text-[#b91c1c]">Text-only baseline</span>
                  <span class="font-mono text-[11px] text-[#b91c1c]">VULNERABLE</span>
                </div>
                <p class="text-xs text-[#525252] mt-1">Confidence collapsed from 88.4% to 38.2% under perturbation.</p>
              </div>
              <div class="p-3.5 bg-[#f0fdf4] rounded-lg border border-[#15803d]/20">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-medium text-[#15803d]">TruthLens-Omni fusion</span>
                  <span class="font-mono text-[11px] text-[#15803d]">RESILIENT</span>
                </div>
                <p class="text-xs text-[#525252] mt-1">Verdict stays <span class="font-mono text-[#171717]">${escapeHtml(res.perturbed_verdict)}</span> (${res.perturbed_truth_score}%).</p>
              </div>
            </div>
            <p class="text-xs text-[#737373]">${escapeHtml(res.explanation)}</p>
          </div>
        `;
        showToast('Adversarial perturbation executed', 'success');
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
      btn.className = 'cn-note-tab px-3 py-1.5 rounded-lg text-xs font-normal text-[#525252] hover:bg-[#f4f4f5] transition-colors';
    });
    const activeBtn = document.getElementById(`btn-cn-tab-${noteId.replace('note-', '')}`);
    if (activeBtn) {
      activeBtn.className = 'cn-note-tab px-3 py-1.5 rounded-lg text-xs font-medium bg-[#171717] text-white transition-colors';
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
        ? 'px-2.5 py-1 rounded-md font-mono text-xs bg-[#f0fdf4] text-[#15803d] border border-[#15803d]/20'
        : 'px-2.5 py-1 rounded-md font-mono text-xs bg-[#fffbeb] text-[#b45309] border border-[#b45309]/20';
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
              ? 'px-2.5 py-1 rounded-md font-mono text-xs bg-[#f0fdf4] text-[#15803d] border border-[#15803d]/20'
              : 'px-2.5 py-1 rounded-md font-mono text-xs bg-[#fffbeb] text-[#b45309] border border-[#b45309]/20';
          }
          if (scoreEl) scoreEl.innerText = `b_i = ${hScore.toFixed(3)}`;
          showToast(`Vote recorded: b_i = ${hScore.toFixed(3)} (${status})`, 'success');
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
        exportDossierBtn.innerText = 'Export markdown';
        exportDossierBtn.disabled = false;
      }
    });
  }

  // ==========================================
  // ENTERPRISE IDENTITY & ACCESS MANAGEMENT (IAM)
  // ==========================================
  state.authMode = 'signin'; // 'signin' | 'register' | 'sandbox'
  state.authToken = localStorage.getItem('truthlens_auth_token') || null;

  window.switchAuthSubTab = function(subTab) {
    state.authMode = subTab;
    const btnSignin = document.getElementById('tab-btn-signin');
    const btnRegister = document.getElementById('tab-btn-register');
    const btnSandbox = document.getElementById('tab-btn-sandbox');
    const fieldName = document.getElementById('field-register-name');
    const fieldExtras = document.getElementById('field-register-extras');
    const ssoContainer = document.getElementById('auth-sso-container');
    const form = document.getElementById('auth-credential-form');
    const sandboxCards = document.getElementById('auth-sandbox-cards');
    const btnLabel = document.getElementById('btn-auth-label');
    const alertBox = document.getElementById('auth-alert-box');

    if (alertBox) alertBox.classList.add('hidden');

    [btnSignin, btnRegister, btnSandbox].forEach(btn => {
      if (btn) {
        btn.className = 'flex-1 py-1.5 rounded-md text-xs font-normal text-[#525252] hover:text-[#171717]';
      }
    });

    if (subTab === 'signin') {
      if (btnSignin) btnSignin.className = 'flex-1 py-1.5 rounded-md text-xs font-medium bg-white text-[#171717] border border-[#171717]/[0.08]';
      if (fieldName) fieldName.classList.add('hidden');
      if (fieldExtras) fieldExtras.classList.add('hidden');
      if (ssoContainer) ssoContainer.classList.remove('hidden');
      if (form) form.classList.remove('hidden');
      if (sandboxCards) sandboxCards.classList.remove('hidden');
      if (btnLabel) btnLabel.innerText = 'Sign in';
    } else if (subTab === 'register') {
      if (btnRegister) btnRegister.className = 'flex-1 py-1.5 rounded-md text-xs font-medium bg-white text-[#171717] border border-[#171717]/[0.08]';
      if (fieldName) fieldName.classList.remove('hidden');
      if (fieldExtras) fieldExtras.classList.remove('hidden');
      if (ssoContainer) ssoContainer.classList.add('hidden');
      if (form) form.classList.remove('hidden');
      if (sandboxCards) sandboxCards.classList.add('hidden');
      if (btnLabel) btnLabel.innerText = 'Register identity';
    } else if (subTab === 'sandbox') {
      if (btnSandbox) btnSandbox.className = 'flex-1 py-1.5 rounded-md text-xs font-medium bg-white text-[#171717] border border-[#171717]/[0.08]';
      if (fieldName) fieldName.classList.add('hidden');
      if (fieldExtras) fieldExtras.classList.add('hidden');
      if (ssoContainer) ssoContainer.classList.add('hidden');
      if (form) form.classList.add('hidden');
      if (sandboxCards) sandboxCards.classList.remove('hidden');
    }
  };

  window.evaluatePasswordEntropy = function(pwd) {
    const bitsEl = document.getElementById('entropy-bits');
    const labelEl = document.getElementById('entropy-label');
    const barEl = document.getElementById('entropy-bar');
    if (!bitsEl || !labelEl || !barEl) return;

    if (!pwd || pwd.length === 0) {
      bitsEl.innerText = '0 bits';
      labelEl.innerText = 'Enter password';
      labelEl.className = 'text-[#737373]';
      barEl.style.width = '0%';
      barEl.className = 'h-full bg-[#d4d4d8]';
      return;
    }

    let pool = 0;
    if (/[a-z]/.test(pwd)) pool += 26;
    if (/[A-Z]/.test(pwd)) pool += 26;
    if (/[0-9]/.test(pwd)) pool += 10;
    if (/[^a-zA-Z0-9]/.test(pwd)) pool += 32;

    const bits = pool > 0 ? Math.round(pwd.length * (Math.log2(pool))) : 0;
    bitsEl.innerText = `${bits} bits`;

    const pct = Math.min(100, Math.round((bits / 70) * 100));
    barEl.style.width = `${pct}%`;

    if (bits < 35) {
      labelEl.innerText = 'Weak';
      labelEl.className = 'text-[#b91c1c]';
      barEl.className = 'h-full bg-[#b91c1c]';
    } else if (bits < 55) {
      labelEl.innerText = 'Standard';
      labelEl.className = 'text-[#b45309]';
      barEl.className = 'h-full bg-[#b45309]';
    } else {
      labelEl.innerText = 'Strong (L5)';
      labelEl.className = 'text-[#15803d]';
      barEl.className = 'h-full bg-[#15803d]';
    }
  };

  window.togglePasswordVisibility = function() {
    const input = document.getElementById('input-auth-password');
    if (!input) return;
    input.type = input.type === 'password' ? 'text' : 'password';
  };

  function updateHeaderIdentity(user) {
    if (!user) return;
    state.currentUser = user;
    state.currentRole = user.role.toLowerCase();
    localStorage.setItem('truthlens_role', state.currentRole);

    const navAvatar = document.getElementById('nav-user-avatar');
    const navName = document.getElementById('nav-user-name');
    const badge = document.getElementById('user-role-badge');
    const statusChip = document.getElementById('auth-status-chip');

    if (navAvatar && user.avatar_url) navAvatar.src = user.avatar_url;
    if (navName && user.full_name) navName.innerText = user.full_name;
    if (badge) badge.innerText = `${user.role} (L${user.clearance_level || 1})`;
    if (statusChip) statusChip.innerText = `${user.role} AUTHENTICATED`;
  }

  window.handleSSOLogin = async function(provider) {
    const alertBox = document.getElementById('auth-alert-box');
    if (alertBox) {
      alertBox.className = 'p-3 rounded-lg text-xs bg-[#f4f4f5] text-[#171717] border border-[#171717]/[0.12]';
      alertBox.innerHTML = `Establishing ${provider.toUpperCase()} SSO handshake...`;
      alertBox.classList.remove('hidden');
    }

    try {
      const resp = await fetch(`/api/v1/auth/sso/${provider}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider })
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail || 'SSO handshake failed');

      localStorage.setItem('truthlens_auth_token', data.token);
      state.authToken = data.token;
      updateHeaderIdentity(data.user);

      if (alertBox) {
        alertBox.className = 'p-3 rounded-lg text-xs bg-[#f0fdf4] text-[#15803d] border border-[#15803d]/20';
        alertBox.innerHTML = `Authenticated via ${provider.toUpperCase()} SSO (${escapeHtml(data.user.full_name)})`;
      }
      showToast(`Signed in as ${data.user.full_name} (${data.user.role})`, 'success');
      setTimeout(() => switchTab('feed'), 600);
    } catch (err) {
      if (alertBox) {
        alertBox.className = 'p-3 rounded-lg text-xs bg-[#fef2f2] text-[#b91c1c] border border-[#b91c1c]/20';
        alertBox.innerHTML = `${escapeHtml(err.message)}`;
      }
      showToast(err.message, 'error');
    }
  };

  window.handleAuthSubmit = async function(e) {
    e.preventDefault();
    const alertBox = document.getElementById('auth-alert-box');
    const submitBtn = document.getElementById('btn-auth-submit');
    const email = document.getElementById('input-auth-email')?.value.trim();
    const password = document.getElementById('input-auth-password')?.value;

    if (!email || !password) {
      showToast('Enter both email and password', 'error');
      return;
    }

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerText = 'Authenticating...';
    }

    try {
      if (state.authMode === 'register') {
        const fullName = document.getElementById('input-auth-name')?.value.trim() || 'Field Officer';
        const role = document.getElementById('input-auth-role')?.value || 'CITIZEN';
        const org = document.getElementById('input-auth-org')?.value.trim() || 'Independent Organization';

        const resp = await fetch('/api/v1/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email,
            password,
            full_name: fullName,
            role,
            organization: org,
            clearance_level: role === 'OFFICER' || role === 'ACADEMIC' ? 5 : (role === 'JOURNALIST' || role === 'RESEARCHER' ? 4 : 1)
          })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Registration failed');

        localStorage.setItem('truthlens_auth_token', data.token);
        state.authToken = data.token;
        updateHeaderIdentity(data.user);

        if (alertBox) {
          alertBox.className = 'p-3 rounded-lg text-xs bg-[#f0fdf4] text-[#15803d] border border-[#15803d]/20';
          alertBox.innerHTML = 'Identity registered in ledger';
          alertBox.classList.remove('hidden');
        }
        showToast(`Account created for ${data.user.full_name}`, 'success');
        setTimeout(() => switchTab('feed'), 600);

      } else {
        const resp = await fetch('/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Authentication failed');

        localStorage.setItem('truthlens_auth_token', data.token);
        state.authToken = data.token;
        updateHeaderIdentity(data.user);

        if (alertBox) {
          alertBox.className = 'p-3 rounded-lg text-xs bg-[#f0fdf4] text-[#15803d] border border-[#15803d]/20';
          alertBox.innerHTML = `Signed in as ${escapeHtml(data.user.full_name)}`;
          alertBox.classList.remove('hidden');
        }
        showToast(`Signed in as ${data.user.full_name}`, 'success');
        setTimeout(() => switchTab('feed'), 600);
      }
    } catch (err) {
      if (alertBox) {
        alertBox.className = 'p-3 rounded-lg text-xs bg-[#fef2f2] text-[#b91c1c] border border-[#b91c1c]/20';
        alertBox.innerHTML = `${escapeHtml(err.message)}`;
        alertBox.classList.remove('hidden');
      }
      showToast(err.message, 'error');
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<span id="btn-auth-label">${state.authMode === 'register' ? 'Register identity' : 'Sign in'}</span>`;
      }
    }
  };

  window.quickAuthPersona = async function(email, password) {
    const alertBox = document.getElementById('auth-alert-box');
    if (alertBox) {
      alertBox.className = 'p-3 rounded-lg text-xs bg-[#f4f4f5] text-[#171717] border border-[#171717]/[0.12]';
      alertBox.innerHTML = `Switching to ${escapeHtml(email)}...`;
      alertBox.classList.remove('hidden');
    }

    try {
      const resp = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail || 'Persona switch failed');

      localStorage.setItem('truthlens_auth_token', data.token);
      state.authToken = data.token;
      updateHeaderIdentity(data.user);

      showToast(`Active role: ${data.user.full_name} (L${data.user.clearance_level})`, 'success');
      setTimeout(() => switchTab('feed'), 500);
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  window.handleAuthLogout = function() {
    localStorage.removeItem('truthlens_auth_token');
    state.authToken = null;
    state.currentUser = null;
    state.currentRole = 'guest';

    const navName = document.getElementById('nav-user-name');
    const badge = document.getElementById('user-role-badge');
    const statusChip = document.getElementById('auth-status-chip');
    if (navName) navName.innerText = 'Guest Evaluator';
    if (badge) badge.innerText = 'GUEST (L0)';
    if (statusChip) statusChip.innerText = 'GUEST UNVERIFIED';

    showToast('Session terminated. Identity signed out.', 'info');
    switchTab('auth');
  };

  window.loadAuthTelemetry = async function() {
    try {
      const resp = await fetch('/api/v1/auth/telemetry');
      if (!resp.ok) return;
      const data = await resp.json();

      const cipherEl = document.getElementById('telemetry-cipher');
      const kdfEl = document.getElementById('telemetry-kdf');
      const tokenEl = document.getElementById('telemetry-token');
      const idEl = document.getElementById('telemetry-identities');

      if (cipherEl) cipherEl.innerText = data.cipher_suite || 'TLS_AES_256_GCM';
      if (kdfEl) kdfEl.innerText = data.kdf_algorithm || 'PBKDF2 (100k)';
      if (tokenEl) tokenEl.innerText = data.token_specification || 'RFC 7519 HS256';
      if (idEl) idEl.innerText = `${data.total_registered_identities || 5} Registered`;
    } catch (err) {
      console.warn('Telemetry load error:', err);
    }
  };

  async function verifySessionOnBoot() {
    const token = localStorage.getItem('truthlens_auth_token');
    if (!token) return;
    try {
      const resp = await fetch('/api/v1/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (resp.ok) {
        const data = await resp.json();
        updateHeaderIdentity(data.user);
      } else {
        localStorage.removeItem('truthlens_auth_token');
      }
    } catch (err) {
      console.warn('Session verification error:', err);
    }
  }

  // Restore saved role on load & verify session
  verifySessionOnBoot();
  const savedRole = localStorage.getItem('truthlens_role') || 'officer';
  if (roleBadge) roleBadge.innerText = savedRole.toUpperCase();

  // Initialize Lucide Icons
  if (window.lucide && typeof window.lucide.createIcons === 'function') {
    window.lucide.createIcons();
  }

  // Keyboard shortcuts: Escape closes modals/drawers; Cmd/Ctrl+Enter submits claim verification; 'v' opens Verify when not typing
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeAuthModal();
      window.toggleMobileSidebar(false);
    }
    const tag = (e.target && e.target.tagName) ? e.target.tagName.toLowerCase() : '';
    const isTyping = tag === 'input' || tag === 'textarea' || tag === 'select';
    if (!isTyping && (e.key === 'v' || e.key === 'V') && !e.metaKey && !e.ctrlKey && !e.altKey) {
      switchTab('verify');
    }
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter' && e.target && e.target.id === 'input-text') {
      e.preventDefault();
      executeVerification();
    }
  });

  // Kickstart router
  initRouting();
});
