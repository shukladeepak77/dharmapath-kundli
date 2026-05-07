function $(id) { return document.getElementById(id); }

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

document.addEventListener("DOMContentLoaded", () => {
  const today = new Date().toISOString().split("T")[0];
  $("muh_start").value = today;
  // Default end = 3 months ahead
  const end = new Date();
  end.setMonth(end.getMonth() + 3);
  $("muh_end").value = end.toISOString().split("T")[0];
});

async function searchLocation() {
  const q = $("muh_location").value.trim();
  if (!q) return;
  $("muh_locationResults").innerHTML = `<div class="loc-item">Searching...</div>`;

  let data = {};
  try {
    const res = await fetch(`/api/location-search?q=${encodeURIComponent(q)}`);
    data = await res.json();
  } catch (_) {}

  if (!data.results || data.results.length === 0) {
    $("muh_locationResults").innerHTML = `<div class="loc-item">No locations found. Enter manually.</div>`;
    return;
  }
  const loc = data.results[0];
  $("muh_latitude").value  = loc.lat;
  $("muh_longitude").value = loc.lng;
  if (loc.gmtOffset !== null && loc.gmtOffset !== undefined) {
    $("muh_timezone").value = loc.gmtOffset;
  }
  $("muh_place").value = loc.display;
  $("muh_locationResults").innerHTML =
    `<div class="loc-item"><strong>✓ ${esc(loc.display)}</strong> &nbsp;·&nbsp; Lat ${esc(loc.lat)}, Lng ${esc(loc.lng)}, TZ ${esc(loc.gmtOffset ?? "—")}</div>`;
}

function qualityIcon(q) {
  if (q === "good" || q === "excellent" || q === "auspicious") return "✓";
  if (q === "inauspicious")  return "✗";
  return "·";
}

function qualityClass(q) {
  if (q === "good" || q === "excellent" || q === "auspicious") return "muh-good";
  if (q === "inauspicious") return "muh-bad";
  return "muh-neutral";
}

function ratingClass(r) {
  if (r === "Excellent") return "muh-rating-excellent";
  if (r === "Good")      return "muh-rating-good";
  return "muh-rating-ok";
}

function formatDate(dateStr) {
  const d = new Date(dateStr + "T12:00:00");
  return d.toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
}

function renderResults(data) {
  if (!data.results || data.results.length === 0) {
    $("muh_results").innerHTML = `<div class="card" style="padding:32px;text-align:center">
      <p style="color:var(--muted);font-size:15px">No auspicious dates found in this range for <strong>${esc(data.event_label)}</strong>.</p>
      <p style="color:var(--muted);font-size:13px;margin-top:8px">Try extending the date range.</p>
    </div>`;
    return;
  }

  const header = `
    <div class="muh-header card">
      <div>
        <h2 class="muh-heading">${esc(data.event_label)}</h2>
        <p class="muh-subheading">${data.total_found} auspicious date${data.total_found !== 1 ? "s" : ""} found${data.place ? " for " + esc(data.place) : ""} · sorted by quality</p>
      </div>
      <div class="muh-legend">
        <span class="muh-legend-item muh-rating-excellent">Excellent</span>
        <span class="muh-legend-item muh-rating-good">Good</span>
        <span class="muh-legend-item muh-rating-ok">Acceptable</span>
      </div>
    </div>`;

  const cards = data.results.map(r => {
    const windows = r.windows.length
      ? r.windows.map(w => `<span class="muh-window">${esc(w.name)}: ${esc(w.start)} – ${esc(w.end)}</span>`).join("")
      : `<span class="muh-window-none">Check individual Choghadiya</span>`;

    return `
      <div class="card muh-card">
        <div class="muh-card-top">
          <div>
            <div class="muh-date">${esc(formatDate(r.date))}</div>
            <div class="muh-sunrise">Sunrise: ${esc(r.sunrise)}</div>
          </div>
          <span class="muh-rating ${ratingClass(r.rating)}">${esc(r.rating)}</span>
        </div>

        <div class="muh-factors">
          <div class="muh-factor ${qualityClass(r.tithi.quality)}">
            <span class="muh-factor-icon">${qualityIcon(r.tithi.quality)}</span>
            <span class="muh-factor-label">Tithi</span>
            <span class="muh-factor-value">${esc(r.tithi.paksha)} ${esc(r.tithi.name)}</span>
          </div>
          <div class="muh-factor ${qualityClass(r.nakshatra.quality)}">
            <span class="muh-factor-icon">${qualityIcon(r.nakshatra.quality)}</span>
            <span class="muh-factor-label">Nakshatra</span>
            <span class="muh-factor-value">${esc(r.nakshatra.name)} (Pada ${r.nakshatra.pada})</span>
          </div>
          <div class="muh-factor ${qualityClass(r.vara.quality)}">
            <span class="muh-factor-icon">${qualityIcon(r.vara.quality)}</span>
            <span class="muh-factor-label">Vara</span>
            <span class="muh-factor-value">${esc(r.vara.name)} (${esc(r.vara.hindi)})</span>
          </div>
          <div class="muh-factor ${qualityClass(r.yoga.quality)}">
            <span class="muh-factor-icon">${qualityIcon(r.yoga.quality)}</span>
            <span class="muh-factor-label">Yoga</span>
            <span class="muh-factor-value">${esc(r.yoga.name)}</span>
          </div>
        </div>

        <div class="muh-windows-row">
          <span class="muh-windows-label">Auspicious windows:</span>
          ${windows}
        </div>
        <div class="muh-avoid-row">
          <span class="muh-avoid-label">Avoid Rahu Kaal:</span>
          <span class="muh-avoid-time">${esc(r.rahu_kaal.start)} – ${esc(r.rahu_kaal.end)}</span>
        </div>
      </div>`;
  }).join("");

  $("muh_results").innerHTML = header + cards;
  $("muh_results").scrollIntoView({ behavior: "smooth", block: "start" });
}

async function submitMuhurat(e) {
  e.preventDefault();

  const lat = parseFloat($("muh_latitude").value);
  const lng = parseFloat($("muh_longitude").value);
  const tz  = parseFloat($("muh_timezone").value);

  if (!lat || !lng || isNaN(tz)) {
    $("muh_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">
      Please search for a location first.</div>`;
    return;
  }

  const payload = {
    event_type:            $("muh_event").value,
    start_date:            $("muh_start").value,
    end_date:              $("muh_end").value,
    latitude:              lat,
    longitude:             lng,
    timezone_offset_hours: tz,
    place:                 $("muh_place").value,
  };

  $("muh_results").innerHTML = `<div class="card" style="padding:36px;text-align:center">
    <div class="spinner"></div>
    <p class="loading-text">Scanning dates for Shubh Muhurat…</p>
    <p class="loading-sub">Reading Tithi, Nakshatra and Choghadiya for each day</p>
  </div>`;

  try {
    const res = await fetch("/api/muhurat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      $("muh_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">${esc(err.detail || "Error finding muhurat.")}</div>`;
      return;
    }
    renderResults(await res.json());
  } catch (_) {
    $("muh_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">An error occurred. Please try again.</div>`;
  }
}

$("muh_searchLocation").addEventListener("click", searchLocation);
$("muhuratForm").addEventListener("submit", submitMuhurat);
