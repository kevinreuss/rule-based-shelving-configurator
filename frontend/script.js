/**
 * Internal Quoting Tool — Frontend Logic (Prototype)
 */

const API_URL = "http://localhost:8000";

const form = document.getElementById("quoteForm");
const submitBtn = document.getElementById("submitBtn");
const loadingEl = document.getElementById("loading");
const errorEl = document.getElementById("error");
const resultsEl = document.getElementById("results");
const configSummary = document.getElementById("configSummary");
const quoteBody = document.getElementById("quoteBody");
const grandTotal = document.getElementById("grandTotal");

function money(value) {
  return "$" + Number(value).toFixed(2);
}

function showLoading() {
  loadingEl.classList.remove("hidden");
  errorEl.classList.add("hidden");
  resultsEl.classList.add("hidden");
  submitBtn.disabled = true;
  submitBtn.textContent = "Generating…";
}

function hideLoading() {
  loadingEl.classList.add("hidden");
  submitBtn.disabled = false;
  submitBtn.textContent = "Generate Quote";
}

function showError(message) {
  errorEl.textContent = message;
  errorEl.classList.remove("hidden");
}

function renderResults(data) {
  // Configuration summary tags
  const summary = data.input_summary;
  configSummary.innerHTML = [
    `Length: ${summary.total_length} m`,
    `Height: ${summary.height} m`,
    `Depth: ${summary.depth} m`,
    `Color: ${summary.frame_color}`,
    `Sections: ${data.sections}`,
    summary.add_back_panel ? "Back Panel" : null,
    summary.add_end_caps ? "End Caps" : null,
  ]
    .filter(Boolean)
    .map((t) => `<span class="tag">${t}</span>`)
    .join("");

  // Table rows
  quoteBody.innerHTML = data.line_items
    .map(
      (item) => `
      <tr>
        <td><code>${item.sku}</code></td>
        <td>${item.component}</td>
        <td class="num">${item.quantity}</td>
        <td class="num">${money(item.unit_price)}</td>
        <td class="num">${money(item.line_total)}</td>
      </tr>`
    )
    .join("");

  grandTotal.textContent = money(data.total);
  resultsEl.classList.remove("hidden");
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  showLoading();

  const payload = {
    total_length: parseInt(document.getElementById("totalLength").value),
    height: parseInt(document.getElementById("height").value),
    depth: parseFloat(document.getElementById("depth").value),
    frame_color: document.getElementById("frameColor").value,
    add_back_panel: document.getElementById("addBackPanel").checked,
    add_end_caps: document.getElementById("addEndCaps").checked,
  };

  try {
    const res = await fetch(`${API_URL}/generate-quote`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(err?.detail || `Server error (${res.status})`);
    }

    const data = await res.json();
    renderResults(data);
  } catch (err) {
    showError(err.message || "Failed to connect to backend. Is it running?");
  } finally {
    hideLoading();
  }
});
