function $(id) { return document.getElementById(id); }

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

async function searchLocation(prefix) {
  const q = $(`${prefix}_location`).value.trim();
  const resultsEl = $(`${prefix}_locationResults`);
  if (!q) return false;
  resultsEl.innerHTML = `<div class="loc-item">Searching…</div>`;

  let data = {};
  try {
    const res = await fetch(`/api/location-search?q=${encodeURIComponent(q)}`);
    data = await res.json();
  } catch (_) {}

  if (!data.results || data.results.length === 0) {
    resultsEl.innerHTML = `<div class="loc-item">No locations found. Enter a valid city name.</div>`;
    return false;
  }
  const loc = data.results[0];
  $(`${prefix}_latitude`).value  = loc.lat;
  $(`${prefix}_longitude`).value = loc.lng;
  if (loc.gmtOffset !== null && loc.gmtOffset !== undefined) {
    $(`${prefix}_timezone`).value = loc.gmtOffset;
  }
  $(`${prefix}_place`).value = loc.display;
  resultsEl.innerHTML =
    `<div class="loc-item"><strong>✓ ${esc(loc.display)}</strong> &nbsp;·&nbsp; Lat ${esc(loc.lat)}, Lng ${esc(loc.lng)}, TZ ${esc(loc.gmtOffset ?? "—")}</div>`;
  return true;
}

function scoreCircleClass(rc) {
  if (rc === "excellent") return "milan-score-excellent";
  if (rc === "good")      return "milan-score-good";
  if (rc === "neutral")   return "milan-score-neutral";
  return "milan-score-bad";
}

function badgeClass(rc) {
  if (rc === "excellent") return "milan-badge-excellent";
  if (rc === "good")      return "milan-badge-good";
  if (rc === "neutral")   return "milan-badge-neutral";
  return "milan-badge-bad";
}

function fillClass(total, max) {
  const r = total / max;
  if (r >= 32 / 36) return "milan-fill-excellent";
  if (r >= 28 / 36) return "milan-fill-very-good";
  if (r >= 24 / 36) return "milan-fill-good";
  if (r >= 18 / 36) return "milan-fill-average";
  return "milan-fill-bad";
}

function kootaClass(q) {
  if (q === "good")    return "milan-koota-good";
  if (q === "bad")     return "milan-koota-bad";
  return "milan-koota-neutral";
}

function renderMilan(data) {
  const boyName  = data.boy.name  || "Boy";
  const girlName = data.girl.name || "Girl";
  const pct      = Math.round(data.total_score / data.max_score * 100);

  const scoreCircle = `
    <div class="milan-score-circle ${scoreCircleClass(data.rating_class)}">
      <div class="milan-score-num">${data.total_score}</div>
      <div class="milan-score-denom">/ ${data.max_score}</div>
    </div>`;

  const resultHeader = `
    <div class="milan-result-header">
      ${scoreCircle}
      <div class="milan-result-info">
        <div class="milan-names">${esc(boyName)} &nbsp;❤&nbsp; ${esc(girlName)}</div>
        <span class="milan-rating-badge ${badgeClass(data.rating_class)}">${esc(data.rating)}</span>
        <p class="milan-summary">${esc(data.summary)}</p>
        <div class="milan-score-bar-wrap">
          <div class="milan-score-bar-label">
            <span>Guna Milan Score</span>
            <span>${data.total_score} / ${data.max_score} (${pct}%)</span>
          </div>
          <div class="milan-score-bar">
            <div class="${fillClass(data.total_score, data.max_score)}" style="width:${pct}%;height:100%;border-radius:4px;"></div>
          </div>
        </div>
      </div>
    </div>`;

  const moonRow = `
    <div class="milan-moon-row">
      <div class="milan-moon-card">
        <div class="milan-moon-person milan-moon-boy">♂ ${esc(boyName)}</div>
        <div class="milan-moon-nak">${esc(data.boy.nak_name)} Pada ${data.boy.pada}</div>
        <div class="milan-moon-rashi">${esc(data.boy.rashi)} · ${esc(data.boy.rashi_hindi)}</div>
      </div>
      <div class="milan-moon-card">
        <div class="milan-moon-person milan-moon-girl">♀ ${esc(girlName)}</div>
        <div class="milan-moon-nak">${esc(data.girl.nak_name)} Pada ${data.girl.pada}</div>
        <div class="milan-moon-rashi">${esc(data.girl.rashi)} · ${esc(data.girl.rashi_hindi)}</div>
      </div>
    </div>`;

  const kootaCards = data.kootas.map(k => `
    <div class="milan-koota-card ${kootaClass(k.quality)}">
      <div class="milan-koota-name">${esc(k.name)}</div>
      <div>
        <span class="milan-koota-score">${k.score}</span>
        <span class="milan-koota-max"> / ${k.max}</span>
      </div>
      <div class="milan-koota-values">Boy: ${esc(k.p1_value)}<br>Girl: ${esc(k.p2_value)}</div>
      <div class="milan-koota-detail">${esc(k.detail)}</div>
    </div>`).join("");

  const kootaGrid = `
    <h3 style="font-family:'Cinzel',serif;font-size:14px;color:var(--brand);margin:0 0 12px">Ashtakoota Guna Milan</h3>
    <div class="milan-koota-grid">${kootaCards}</div>`;

  const doshaKootas = data.kootas.filter(k => k.dosha);
  let doshaSection;
  if (doshaKootas.length > 0) {
    const doshaCards = doshaKootas.map(k => `
      <div class="milan-dosha-card">
        <div class="milan-dosha-name">⚠ ${esc(k.name)} Dosha</div>
        <p class="milan-dosha-text">${esc(k.detail)}</p>
      </div>`).join("");
    doshaSection = `
      <div>
        <h3 class="milan-doshas-heading">Dosha Warnings</h3>
        ${doshaCards}
        <p style="font-size:12px;color:var(--muted);margin:8px 0 0">Consult a qualified Jyotishi for remedies and guidance.</p>
      </div>`;
  } else {
    doshaSection = `
      <div class="milan-no-dosha">✓ No major Doshas — Nadi, Bhakoot and Gana are all compatible.</div>`;
  }

  $("milan_results").innerHTML = `
    <div class="card">
      ${resultHeader}
      ${moonRow}
      ${kootaGrid}
      ${doshaSection}
    </div>`;

  $("milan_results").scrollIntoView({ behavior: "smooth", block: "start" });
}

async function submitMilan(e) {
  e.preventDefault();

  if (!$("b_latitude").value && $("b_location").value.trim()) {
    const found = await searchLocation("b");
    if (!found) {
      $("milan_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">Boy's birth location not found. Please enter a valid city name.</div>`;
      return;
    }
  }
  if (!$("g_latitude").value && $("g_location").value.trim()) {
    const found = await searchLocation("g");
    if (!found) {
      $("milan_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">Girl's birth location not found. Please enter a valid city name.</div>`;
      return;
    }
  }

  const bTz = parseFloat($("b_timezone").value);
  const gTz = parseFloat($("g_timezone").value);

  if (!$("b_latitude").value || !$("b_longitude").value || isNaN(bTz)) {
    $("milan_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">Please enter the boy's birth location.</div>`;
    return;
  }
  if (!$("g_latitude").value || !$("g_longitude").value || isNaN(gTz)) {
    $("milan_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">Please enter the girl's birth location.</div>`;
    return;
  }

  const payload = {
    boy_name:  $("b_name").value.trim(),
    boy_date:  $("b_date").value,
    boy_time:  $("b_time").value,
    boy_tz:    bTz,
    girl_name: $("g_name").value.trim(),
    girl_date: $("g_date").value,
    girl_time: $("g_time").value,
    girl_tz:   gTz,
  };

  $("milan_results").innerHTML = `<div class="card" style="padding:36px;text-align:center">
    <div class="spinner"></div>
    <p class="loading-text">Calculating Kundli Milan…</p>
    <p class="loading-sub">Computing Ashtakoota Guna compatibility</p>
  </div>`;

  try {
    const res = await fetch("/api/kundli-milan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      $("milan_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">${esc(err.detail || "Error calculating Milan.")}</div>`;
      return;
    }
    renderMilan(await res.json());
  } catch (_) {
    $("milan_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">An error occurred. Please try again.</div>`;
  }
}

$("milanForm").addEventListener("submit", submitMilan);
