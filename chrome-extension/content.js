/**
 * TruthLens-Omni In-Page Content Script.
 * Detects selected text on web pages and displays a non-intrusive factual nutrition chip.
 */

let floatingChip = null;

function removeFloatingChip() {
  if (floatingChip) {
    floatingChip.remove();
    floatingChip = null;
  }
}

document.addEventListener("mouseup", (e) => {
  const selection = window.getSelection().toString().trim();
  if (!selection || selection.length < 20 || selection.length > 500) {
    removeFloatingChip();
    return;
  }

  // Remove existing
  removeFloatingChip();

  // Create floating trigger chip
  floatingChip = document.createElement("div");
  floatingChip.id = "truthlens-floating-trigger";
  floatingChip.innerHTML = "🔍 Audit with TruthLens";
  floatingChip.style.position = "absolute";
  floatingChip.style.left = `${e.pageX + 10}px`;
  floatingChip.style.top = `${e.pageY - 35}px`;
  floatingChip.style.background = "#111622";
  floatingChip.style.color = "#ffffff";
  floatingChip.style.fontSize = "11px";
  floatingChip.style.fontWeight = "600";
  floatingChip.style.padding = "5px 10px";
  floatingChip.style.borderRadius = "20px";
  floatingChip.style.boxShadow = "0 4px 12px rgba(0,0,0,0.2)";
  floatingChip.style.cursor = "pointer";
  floatingChip.style.zIndex = "999999";
  floatingChip.style.border = "1px solid rgba(255,255,255,0.15)";
  floatingChip.style.transition = "transform 0.15s ease";

  floatingChip.addEventListener("mouseenter", () => {
    floatingChip.style.transform = "scale(1.05)";
  });
  floatingChip.addEventListener("mouseleave", () => {
    floatingChip.style.transform = "scale(1.0)";
  });

  floatingChip.addEventListener("click", async () => {
    floatingChip.innerHTML = "Auditing...";
    try {
      const resp = await fetch("http://127.0.0.1:8000/api/v1/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: selection,
          publication_date: new Date().toISOString(),
        }),
      });

      const res = await resp.json();
      const color = res.verdict === "VERIFIED" ? "#10B981" : (res.verdict === "REFUTED" ? "#EF4444" : "#F59E0B");

      floatingChip.innerHTML = `
        <span style="color:${color}; font-weight:bold;">[${res.verdict}]</span> 
        Truth: ${(res.confidence_score * 100).toFixed(0)}%
      `;
    } catch (err) {
      floatingChip.innerHTML = "Server Offline (127.0.0.1:8000)";
    }
  });

  document.body.appendChild(floatingChip);
});

document.addEventListener("mousedown", (e) => {
  if (floatingChip && !floatingChip.contains(e.target)) {
    removeFloatingChip();
  }
});
