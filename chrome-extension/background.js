/**
 * TruthLens-Omni Background Service Worker.
 * Handles Context Menu actions for verifying highlighted claims across web pages.
 */

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "truthlens-verify-selection",
    title: "Verify Claim with TruthLens-Omni",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "truthlens-verify-selection" && info.selectionText) {
    const text = info.selectionText.trim();
    try {
      const resp = await fetch("http://127.0.0.1:8000/api/v1/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          publication_date: new Date().toISOString()
        })
      });
      const data = await resp.json();

      // Show Chrome desktop notification
      if (chrome.notifications) {
        chrome.notifications.create({
          type: "basic",
          iconUrl: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='48' height='48'><rect width='48' height='48' rx='10' fill='%235E4BF5'/><text x='12' y='32' font-size='22' font-family='sans-serif' font-weight='bold' fill='white'>TL</text></svg>",
          title: `TruthLens: ${data.verdict}`,
          message: data.nutrition_card ? data.nutrition_card.summary_statement : `Calibrated Truth Score: ${(data.confidence_score * 100).toFixed(1)}%`
        });
      }
    } catch (err) {
      console.warn("TruthLens context menu verification error:", err);
    }
  }
});

