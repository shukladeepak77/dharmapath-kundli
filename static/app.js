let lastResult = null;
let currentChart = "d1";

document.addEventListener("DOMContentLoaded", () => {
  $("birth_time").value = "12:00";
});

const PLANET_FULL_NAMES = {
  "La": "Lagna",         "Su": "Sun / Surya",      "Mo": "Moon / Chandra",
  "Ma": "Mars / Mangal", "Me": "Mercury / Budh",    "Ju": "Jupiter / Guru",
  "Ve": "Venus / Shukra","Sa": "Saturn / Shani",    "Ra": "Rahu",
  "Ke": "Ketu",
};

const PLANET_COLORS = {
  "La": "#7c2d12", "Su": "#dc2626", "Mo": "#2563eb", "Ma": "#b91c1c",
  "Me": "#059669", "Ju": "#d97706", "Ve": "#7c3aed", "Sa": "#374151",
  "Ra": "#0891b2", "Ke": "#78350f",
};

const housePositions = {
  1: [50, 13], 2: [25, 12], 3: [13, 25], 4: [15, 50],
  5: [13, 75], 6: [25, 88], 7: [50, 87], 8: [75, 88],
  9: [87, 75], 10: [85, 50], 11: [87, 25], 12: [75, 12],
};


function $(id) { return document.getElementById(id); }

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function degreeText(value) {
  const d = Math.floor(value);
  const m = Math.floor((value - d) * 60);
  return `${String(d).padStart(2, "0")}°${String(m).padStart(2, "0")}'`;
}

async function searchLocation() {
  const q = $("location").value.trim();
  if (!q) return false;

  $("locationResults").innerHTML = `<div class="loc-item">Searching...</div>`;

  let data = {};
  try {
    const res = await fetch(`/api/location-search?q=${encodeURIComponent(q)}`);
    data = await res.json();
  } catch (_) {}

  if (!data.results || data.results.length === 0) {
    $("locationResults").innerHTML = `<div class="loc-item">No locations found. Enter latitude/longitude manually.</div>`;
    return false;
  }

  const loc = data.results[0];
  $("latitude").value = loc.lat;
  $("longitude").value = loc.lng;
  if (loc.gmtOffset !== null && loc.gmtOffset !== undefined) {
    $("timezone").value = loc.gmtOffset;
  }
  $("place").value = loc.display;
  $("locationResults").innerHTML = `<div class="loc-item"><strong>✓ ${esc(loc.display)}</strong> &nbsp;·&nbsp; Lat ${esc(loc.lat)}, Lng ${esc(loc.lng)}, TZ ${esc(loc.gmtOffset ?? "—")}</div>`;
  return true;
}

function renderSummary(result) {
  const bd = result.birth_data;
  $("summary").innerHTML = `
    <h2>Kundli Report</h2>
    <div class="summary-grid">
      <div class="summary-item"><span>Birth</span>${esc(bd.birth_datetime_local)}</div>
      <div class="summary-item"><span>Place</span>${esc(bd.place)}</div>
      <div class="summary-item"><span>UTC</span>${esc(result.utc_datetime)}</div>
      <div class="summary-item"><span>Ayanamsha</span>${esc(result.ayanamsha_lahiri)}</div>
      <div class="summary-item"><span>Julian Day</span>${esc(result.julian_day_ut)}</div>
    </div>
  `;
}

function renderChart(chartData) {
  const houses = chartData.houses;
  let html = `
    <svg viewBox="0 0 100 100" preserveAspectRatio="none">
      <line x1="0" y1="0" x2="100" y2="100" stroke="#7c2d12" stroke-width="0.6"/>
      <line x1="100" y1="0" x2="0" y2="100" stroke="#7c2d12" stroke-width="0.6"/>
      <line x1="50" y1="0" x2="100" y2="50" stroke="#7c2d12" stroke-width="0.6"/>
      <line x1="100" y1="50" x2="50" y2="100" stroke="#7c2d12" stroke-width="0.6"/>
      <line x1="50" y1="100" x2="0" y2="50" stroke="#7c2d12" stroke-width="0.6"/>
      <line x1="0" y1="50" x2="50" y2="0" stroke="#7c2d12" stroke-width="0.6"/>
    </svg>
  `;

  for (let i = 1; i <= 12; i++) {
    const h = houses[String(i)];
    const [x, y] = housePositions[i];

    const planetsHtml = h.planets.map(p => {
      const raw = p.short;
      const isRetro = raw.endsWith("R") && (raw.slice(0, -1) in PLANET_FULL_NAMES);
      const key = isRetro ? raw.slice(0, -1) : raw;
      const fullName = (PLANET_FULL_NAMES[key] || raw) + (isRetro ? " ℞" : "");
      const color = PLANET_COLORS[key] || "#111827";
      return `<div class="planet-line" style="color:${color}">${fullName}</div>`;
    }).join("");

    const lagnaMarker = i === 1 ? '<div class="lagna-dot"></div>' : "";

    html += `
      <div class="house-label" style="left:${x}%; top:${y}%;">
        ${lagnaMarker}
        <div class="rashi-num">${h.rashi_number}</div>
        <div class="planets">${planetsHtml}</div>
        <div class="house-name">H${i} ${h.rashi}</div>
      </div>
    `;
  }

  $("northChart").innerHTML = html;
}

function positionsTable(positions) {
  const order = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
  return `
    <table class="table">
      <thead><tr><th>Planet</th><th>Rashi</th><th>Degree</th><th>House</th><th>Nakshatra</th><th>Pada</th></tr></thead>
      <tbody>
        ${order.map(p => {
          const x = positions[p];
          const color = PLANET_COLORS[p === "Lagna" ? "La" : p.slice(0,2)] || "#78716c";
          const dot = `<span class="planet-dot" style="background:${color}"></span>`;
          const retro = x.retrograde && !["Lagna","Rahu","Ketu"].includes(p) ? " ℞" : "";
          return `<tr>
            <td><strong>${dot}${esc(p)}${retro}</strong></td>
            <td>${esc(x.rashi)}</td>
            <td>${degreeText(x.degree_in_rashi)}</td>
            <td>${x.house}</td>
            <td>${esc(x.nakshatra)}</td>
            <td>${x.pada}</td>
          </tr>`;
        }).join("")}
      </tbody>
    </table>
  `;
}

function renderPositions(result) {
  const positions = currentChart === "d1" ? result.d1_rashi_chart : result.d9_navamsa_chart;
  $("positions").innerHTML = positionsTable(positions);
}

function renderDashas(result) {
  $("dashas").innerHTML = `
    <table class="table">
      <thead><tr><th>Lord</th><th>Start</th><th>End</th><th>Years</th></tr></thead>
      <tbody>
        ${result.vimshottari_mahadasha.map(d => {
          const color = PLANET_COLORS[d.lord.slice(0,2)] || "#78716c";
          const dot = `<span class="planet-dot" style="background:${color}"></span>`;
          return `<tr>
            <td><strong>${dot}${esc(d.lord)}</strong></td>
            <td>${esc(d.start)}</td>
            <td>${esc(d.end)}</td>
            <td>${d.years}</td>
          </tr>`;
        }).join("")}
      </tbody>
    </table>
  `;
}

function renderAll(result) {
  renderSummary(result);
  const chart = currentChart === "d1" ? result.d1_chart_visual : result.d9_chart_visual;
  renderChart(chart);
  renderPositions(result);
  renderDashas(result);
  document.querySelectorAll(".results .card, .results .chart-tabs").forEach(el => {
    el.classList.remove("fade-in");
    void el.offsetWidth;
    el.classList.add("fade-in");
  });
}

async function generateKundli(event) {
  event.preventDefault();

  // Auto-search location if lat/lng not yet filled
  if (!$("latitude").value && $("location").value.trim()) {
    const found = await searchLocation();
    if (!found) {
      $("summary").innerHTML = `<div class="loading-state">
        <p style="color:#9a3412;font-weight:700">Location not found. Please enter a valid place or fill latitude/longitude manually.</p>
      </div>`;
      return;
    }
  }

  const payload = {
    birth_date: $("birth_date").value,
    birth_time: $("birth_time").value,
    place: $("place").value,
    latitude: $("latitude").value,
    longitude: $("longitude").value,
    timezone_offset_hours: $("timezone").value,
  };

  $("summary").innerHTML = `
    <div class="loading-state">
      <div class="spinner"></div>
      <p class="loading-text">Calculating your Kundli…</p>
      <p class="loading-sub">Reading planetary positions</p>
    </div>`;

  const res = await fetch("/api/generate-kundli", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json();
    $("summary").innerHTML = `
      <div style="padding:20px;text-align:center">
        <p style="color:#9a3412;font-weight:700;font-size:16px;margin:0 0 8px">Unable to generate Kundli</p>
        <p style="color:#78716c;font-size:14px;margin:0">${esc(err.detail || "Please check all fields and try again.")}</p>
      </div>`;
    return;
  }

  lastResult = await res.json();
  renderAll(lastResult);
}

async function downloadJson() {
  const btn = $("downloadJson");
  const payload = {
    birth_date: $("birth_date").value,
    birth_time: $("birth_time").value,
    place: $("place").value,
    latitude: $("latitude").value,
    longitude: $("longitude").value,
    timezone_offset_hours: $("timezone").value,
  };

  btn.textContent = "Generating…";
  btn.disabled = true;

  try {
    const res = await fetch("/generate-file", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      alert("Failed to generate PDF. Please fill in all fields and try again.");
      return;
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `kundli_${payload.birth_date}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } finally {
    btn.textContent = "Download Kundli";
    btn.disabled = false;
  }
}

$("kundliForm").addEventListener("submit", generateKundli);
$("downloadJson").addEventListener("click", downloadJson);

document.querySelectorAll(".tab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
    btn.classList.add("active");
    currentChart = btn.dataset.chart;
    if (lastResult) renderAll(lastResult);
  });
});
