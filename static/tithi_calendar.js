function $(id) { return document.getElementById(id); }

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

const MONTH_NAMES = ["January","February","March","April","May","June",
                     "July","August","September","October","November","December"];

document.addEventListener("DOMContentLoaded", () => {
  const now = new Date();
  const sel = $("cal_month");
  MONTH_NAMES.forEach((name, i) => {
    const opt = document.createElement("option");
    opt.value = i + 1;
    opt.textContent = name;
    if (i + 1 === now.getMonth() + 1) opt.selected = true;
    sel.appendChild(opt);
  });
  $("cal_year").value = now.getFullYear();
});

let _locTimer = null;

function _fillLocation(loc) {
  $("cal_latitude").value  = loc.lat;
  $("cal_longitude").value = loc.lng;
  $("cal_timezone").value  = loc.gmtOffset;
  $("cal_place").value     = loc.display;
  $("cal_location").value  = loc.display;
  $("cal_locationResults").innerHTML = "";
}

$("cal_location").addEventListener("input", () => {
  $("cal_latitude").value = "";
  clearTimeout(_locTimer);
  const q = $("cal_location").value.trim();
  if (q.length < 2) { $("cal_locationResults").innerHTML = ""; return; }
  _locTimer = setTimeout(async () => {
    $("cal_locationResults").innerHTML = `<div class="loc-item">Searching…</div>`;
    try {
      const res  = await fetch(`/api/location-search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      if (!data.results || !data.results.length) {
        $("cal_locationResults").innerHTML = `<div class="loc-item">No results found.</div>`;
        return;
      }
      $("cal_locationResults").innerHTML = data.results
        .map(l => `<div class="loc-item" style="cursor:pointer">${esc(l.display)}</div>`)
        .join("");
      document.querySelectorAll("#cal_locationResults .loc-item").forEach((el, i) => {
        el.addEventListener("click", () => _fillLocation(data.results[i]));
      });
    } catch (_) { $("cal_locationResults").innerHTML = ""; }
  }, 400);
});

function calDayClass(tithis) {
  const t = tithis[0];
  if (t.name === "Purnima")  return "cal-day cal-purnima";
  if (t.name === "Amavasya") return "cal-day cal-amavasya";
  if (t.paksha === "Shukla") return "cal-day cal-shukla";
  return "cal-day cal-krishna";
}

function renderCalendar(data) {
  const DAY_HEADERS = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];

  let html = `
    <div class="card cal-card">
      <h3 class="cal-heading">${esc(data.month_name)} ${data.year}${data.place ? " · " + esc(data.place) : ""}</h3>
      <div class="cal-legend">
        <span class="cal-leg-shukla">Shukla Paksha</span>
        <span class="cal-leg-krishna">Krishna Paksha</span>
        <span class="cal-leg-purnima">Purnima</span>
        <span class="cal-leg-amavasya">Amavasya</span>
      </div>
      <div class="cal-grid">`;

  DAY_HEADERS.forEach(d => { html += `<div class="cal-hdr">${d}</div>`; });

  const firstWeekday = data.days[0].weekday;
  for (let i = 0; i < firstWeekday; i++) {
    html += `<div class="cal-day cal-empty"></div>`;
  }

  data.days.forEach(day => {
    const t1 = day.tithis[0];
    const t2 = day.tithis[1];
    html += `<div class="${calDayClass(day.tithis)}">
      <div class="cal-day-num">${day.day}</div>
      <div class="cal-tithi-main">${esc(t1.name)}</div>
      <div class="cal-tithi-sub">${t1.paksha === "Shukla" ? "S" : "K"}${t1.number}${t1.upto ? " · till " + esc(t1.upto) : ""}</div>
      ${t2 ? `<div class="cal-tithi-main cal-tithi2">${esc(t2.name)}</div><div class="cal-tithi-sub">${t2.paksha === "Shukla" ? "S" : "K"}${t2.number} · from ${esc(t2.from)}</div>` : ""}
    </div>`;
  });

  html += `</div></div>`;
  $("cal_results").innerHTML = html;
}

async function submitCalendar(e) {
  e.preventDefault();

  if (!$("cal_latitude").value) {
    const q = $("cal_location").value.trim();
    if (!q) {
      $("cal_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">Please enter a location.</div>`;
      return;
    }
    $("cal_results").innerHTML = `<div class="card" style="padding:28px;text-align:center">
      <div class="spinner"></div><p class="loading-text">Finding location…</p></div>`;
    try {
      const res  = await fetch(`/api/location-search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      if (!data.results || !data.results.length) {
        $("cal_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">Location not found. Please try a different name.</div>`;
        return;
      }
      _fillLocation(data.results[0]);
    } catch (_) {
      $("cal_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">Location lookup failed. Please try again.</div>`;
      return;
    }
  }

  const payload = {
    year:                  parseInt($("cal_year").value),
    month:                 parseInt($("cal_month").value),
    latitude:              parseFloat($("cal_latitude").value),
    longitude:             parseFloat($("cal_longitude").value),
    timezone_offset_hours: parseFloat($("cal_timezone").value),
    place:                 $("cal_place").value,
  };

  $("cal_results").innerHTML = `<div class="card" style="padding:28px;text-align:center">
    <div class="spinner"></div>
    <p class="loading-text">Building Tithi Calendar…</p></div>`;

  try {
    const res = await fetch("/api/panchang-month", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      $("cal_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">${esc(err.detail || "Error generating calendar.")}</div>`;
      return;
    }
    renderCalendar(await res.json());
    $("cal_results").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (_) {
    $("cal_results").innerHTML = `<div class="card" style="padding:20px;text-align:center;color:#9a3412">An error occurred. Please try again.</div>`;
  }
}

$("calForm").addEventListener("submit", submitCalendar);
