/**
 * TruthLens-Omni Browser Extension Popup Controller.
 * Communicates with localhost:8000/api/v1/verify and /api/v1/scrape.
 */

const API_BASE = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
  const verifyTabBtn = document.getElementById("btn-verify-tab");
  const verifyTextBtn = document.getElementById("btn-verify-text");
  const inputTextArea = document.getElementById("popup-input-text");
  const resultCard = document.getElementById("popup-result");
  const verdictBadge = document.getElementById("popup-verdict-badge");
  const truthScoreEl = document.getElementById("popup-truth-score");
  const freshnessEl = document.getElementById("popup-freshness");
  const nutritionEl = document.getElementById("popup-nutrition");

  // Audit Active Tab
  verifyTabBtn.addEventListener("click", async () => {
    verifyTabBtn.innerText = "Extracting Page...";
    verifyTabBtn.disabled = true;

    try {
      if (chrome && chrome.tabs) {
        chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
          if (!tabs || tabs.length === 0) return alert("Could not access active tab.");
          const activeTab = tabs[0];
          const url = activeTab.url;

          // Call scrape & verify
          const scrapeResp = await fetch(`${API_BASE}/api/v1/scrape`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url }),
          });

          const scrapeData = await scrapeResp.json();
          if (scrapeData.status === "success" && scrapeData.body_text) {
            inputTextArea.value = scrapeData.body_text.slice(0, 300);
            await executeVerification(scrapeData.body_text, scrapeData.domain);
          } else {
            // Fallback to tab title
            await executeVerification(activeTab.title, activeTab.url);
          }
        });
      } else {
        alert("Chrome Tabs API not active in this environment.");
      }
    } catch (err) {
      alert("Error auditing tab: " + err.message);
    } finally {
      verifyTabBtn.innerText = "⚡ Audit Active Tab";
      verifyTabBtn.disabled = false;
    }
  });

  // Audit Custom Text
  verifyTextBtn.addEventListener("click", async () => {
    const text = inputTextArea.value.trim();
    if (!text) return alert("Please enter text or a claim to verify.");

    verifyTextBtn.innerText = "Running TruthLens...";
    verifyTextBtn.disabled = true;

    try {
      await executeVerification(text);
    } catch (err) {
      alert("Verification error: " + err.message);
    } finally {
      verifyTextBtn.innerText = "Audit Assertion";
      verifyTextBtn.disabled = false;
    }
  });

  async function executeVerification(text, publisher) {
    const resp = await fetch(`${API_BASE}/api/v1/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        publisher,
        publication_date: new Date().toISOString(),
      }),
    });

    if (!resp.ok) throw new Error("TruthLens server returned HTTP " + resp.status);

    const data = await resp.json();
    renderResult(data);
  }

  function renderResult(data) {
    resultCard.style.display = "block";
    verdictBadge.innerText = data.verdict;
    verdictBadge.className = `verdict-badge verdict-${data.verdict}`;
    truthScoreEl.innerText = `${(data.confidence_score * 100).toFixed(1)}%`;
    freshnessEl.innerText = `w(t) = ${(data.temporal_freshness_weight || 0.95).toFixed(2)}`;

    if (data.nutrition_card) {
      nutritionEl.innerText = data.nutrition_card.summary_statement;
    } else {
      nutritionEl.innerText = data.explanation || "No contextual statement generated.";
    }
  }
});
