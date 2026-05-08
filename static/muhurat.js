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

let _locTimer = null;

function _fillLocation(loc) {
  $("muh_latitude").value  = loc.lat;
  $("muh_longitude").value = loc.lng;
  $("muh_timezone").value  = loc.gmtOffset;
  $("muh_place").value     = loc.display;
  $("muh_location").value  = loc.display;
  $("muh_locationResults").innerHTML = "";
}

$("muh_location").addEventListener("input", () => {
  $("muh_latitude").value = "";
  clearTimeout(_locTimer);
  const q = $("muh_location").value.trim();
  if (q.length < 2) { $("muh_locationResults").innerHTML = ""; return; }
  _locTimer = setTimeout(async () => {
    $("muh_locationResults").innerHTML = `<div class="loc-item">Searching…</div>`;
    try {
      const res  = await fetch(`/api/location-search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      if (!data.results || !data.results.length) {
        $("muh_locationResults").innerHTML = `<div class="loc-item">No results found.</div>`;
        return;
      }
      $("muh_locationResults").innerHTML = data.results
        .map(l => `<div class="loc-item" style="cursor:pointer">${esc(l.display)}</div>`)
        .join("");
      document.querySelectorAll("#muh_locationResults .loc-item").forEach((el, i) => {
        el.addEventListener("click", () => _fillLocation(data.results[i]));
      });
    } catch (_) { $("muh_locationResults").innerHTML = ""; }
  }, 400);
});

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

  const disclaimer = `
    <div class="card muh-disclaimer">
      <h3 class="muh-disclaimer-title">How These Dates Are Calculated</h3>
      <p class="muh-disclaimer-body">
        Muhurat suggestions are based on classical Vedic Jyotisha principles — evaluating
        <strong>Tithi</strong> (lunar day), <strong>Nakshatra</strong> (lunar mansion),
        <strong>Vara</strong> (weekday) and <strong>Yoga</strong> for each date, weighted
        according to traditional rules for the selected event type. Auspicious time windows
        within the day are drawn from <strong>Choghadiya</strong>, filtered to exclude
        Rahu Kaal, Yamgandam and Gulikai.
      </p>
      <div class="muh-disclaimer-notice">
        <strong>Important:</strong> These suggestions are based on general classical Jyotisha
        rules and do <em>not</em> account for individual birth charts, regional traditions,
        family customs, or the specific planetary periods (Dasha) of the individuals involved.
        For important life events, we strongly encourage consulting a qualified Jyotishi who
        can assess the full horoscope. All results are provided for
        <strong>informational and spiritual exploration purposes only</strong> and do not
        constitute professional astrological advice. AstroJyotisha and Dharma Path USA
        Foundation make no representations or warranties regarding the accuracy or fitness
        of these suggestions for any particular purpose.
      </div>
      <p class="muh-disclaimer-seva">Offered as seva by Dharma Path USA Foundation &nbsp;·&nbsp; <a href="mailto:seva@dharmpathusa.com">seva@dharmpathusa.com</a></p>
    </div>`;

  $("muh_results").innerHTML = header + cards + disclaimer;
  $("muh_results").scrollIntoView({ behavior: "smooth", block: "start" });
}

async function submitMuhurat(e) {
  e.preventDefault();

  // Auto-resolve location if user typed but didn't pick from suggestions
  if (!$("muh_latitude").value) {
    const q = $("muh_location").value.trim();
    if (!q) {
      $("muh_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">Please enter a location.</div>`;
      return;
    }
    $("muh_results").innerHTML = `<div class="card" style="padding:36px;text-align:center">
      <div class="spinner"></div><p class="loading-text">Finding location…</p></div>`;
    try {
      const res  = await fetch(`/api/location-search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      if (!data.results || !data.results.length) {
        $("muh_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">Location not found. Please try a different name.</div>`;
        return;
      }
      _fillLocation(data.results[0]);
    } catch (_) {
      $("muh_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">Location lookup failed. Please try again.</div>`;
      return;
    }
  }

  const payload = {
    event_type:            $("muh_event").value,
    start_date:            $("muh_start").value,
    end_date:              $("muh_end").value,
    latitude:              parseFloat($("muh_latitude").value),
    longitude:             parseFloat($("muh_longitude").value),
    timezone_offset_hours: parseFloat($("muh_timezone").value),
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

$("muhuratForm").addEventListener("submit", submitMuhurat);
