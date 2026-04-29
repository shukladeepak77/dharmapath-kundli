let lastResult = null;
let currentChart = "d1";

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

function degreeText(value) {
  const d = Math.floor(value);
  const m = Math.floor((value - d) * 60);
  return `${String(d).padStart(2, "0")}°${String(m).padStart(2, "0")}'`;
}

async function searchLocation() {
  const q = $("location").value.trim();
  if (!q) return;

  $("locationResults").innerHTML = `<div class="loc-item">Searching...</div>`;

  const res = await fetch(`/api/location-search?q=${encodeURIComponent(q)}`);
  const data = await res.json();

  if (!data.results || data.results.length === 0) {
    $("locationResults").innerHTML = `<div class="loc-item">No locations found. Enter latitude/longitude manually.</div>`;
    return;
  }

  $("locationResults").innerHTML = data.results.map((loc, idx) => `
    <div class="loc-item" data-idx="${idx}">
      <strong>${loc.display}</strong><br>
      Lat ${loc.lat}, Lng ${loc.lng}, TZ ${loc.gmtOffset ?? "manual"}
    </div>
  `).join("");

  document.querySelectorAll(".loc-item").forEach(el => {
    el.addEventListener("click", () => {
      const loc = data.results[Number(el.dataset.idx)];
      $("latitude").value = loc.lat;
      $("longitude").value = loc.lng;
      if (loc.gmtOffset !== null && loc.gmtOffset !== undefined) {
        $("timezone").value = loc.gmtOffset;
      }
      $("place").value = loc.display;
      $("locationResults").innerHTML = `<div class="loc-item">Selected: ${loc.display}</div>`;
    });
  });
}

function renderSummary(result) {
  const bd = result.birth_data;
  $("summary").innerHTML = `
    <h2>Kundli Report</h2>
    <div class="summary-grid">
      <div class="summary-item"><span>Birth</span>${bd.birth_datetime_local}</div>
      <div class="summary-item"><span>Place</span>${bd.place}</div>
      <div class="summary-item"><span>UTC</span>${result.utc_datetime}</div>
      <div class="summary-item"><span>Ayanamsha</span>${result.ayanamsha_lahiri}</div>
      <div class="summary-item"><span>Julian Day</span>${result.julian_day_ut}</div>
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
          return `<tr>
            <td><strong>${p}${x.retrograde && !["Lagna","Rahu","Ketu"].includes(p) ? " ℞" : ""}</strong></td>
            <td>${x.rashi}</td>
            <td>${degreeText(x.degree_in_rashi)}</td>
            <td>${x.house}</td>
            <td>${x.nakshatra}</td>
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
        ${result.vimshottari_mahadasha.map(d => `
          <tr><td><strong>${d.lord}</strong></td><td>${d.start}</td><td>${d.end}</td><td>${d.years}</td></tr>
        `).join("")}
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
}

async function generateKundli(event) {
  event.preventDefault();

  const payload = {
    birth_date: $("birth_date").value,
    birth_time: $("birth_time").value,
    place: $("place").value,
    latitude: $("latitude").value,
    longitude: $("longitude").value,
    timezone_offset_hours: $("timezone").value,
  };

  $("summary").innerHTML = `<h2>Calculating...</h2><p>Please wait.</p>`;

  const res = await fetch("/api/generate-kundli", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json();
    $("summary").innerHTML = `<h2>Error</h2><p>${err.detail || "Failed to generate kundli."}</p>`;
    return;
  }

  lastResult = await res.json();
  renderAll(lastResult);
}

function downloadJson() {
  const form = document.createElement("form");
  form.method = "POST";
  form.action = "/generate-file";

  const fields = {
    birth_date: $("birth_date").value,
    birth_time: $("birth_time").value,
    place: $("place").value,
    latitude: $("latitude").value,
    longitude: $("longitude").value,
    timezone_offset_hours: $("timezone").value,
  };

  for (const [key, value] of Object.entries(fields)) {
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = key;
    input.value = value;
    form.appendChild(input);
  }

  document.body.appendChild(form);
  form.submit();
  form.remove();
}

$("searchLocation").addEventListener("click", searchLocation);
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
