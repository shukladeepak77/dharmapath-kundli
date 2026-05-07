function $(id) { return document.getElementById(id); }

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

document.addEventListener("DOMContentLoaded", () => {
  $("pan_date").value = new Date().toISOString().split("T")[0];
});

async function searchLocation() {
  const q = $("pan_location").value.trim();
  if (!q) return;
  $("pan_locationResults").innerHTML = `<div class="loc-item">Searching...</div>`;

  let data = {};
  try {
    const res = await fetch(`/api/location-search?q=${encodeURIComponent(q)}`);
    data = await res.json();
  } catch (_) {}

  if (!data.results || data.results.length === 0) {
    $("pan_locationResults").innerHTML = `<div class="loc-item">No locations found. Enter manually.</div>`;
    return;
  }

  const loc = data.results[0];
  $("pan_latitude").value  = loc.lat;
  $("pan_longitude").value = loc.lng;
  if (loc.gmtOffset !== null && loc.gmtOffset !== undefined) {
    $("pan_timezone").value = loc.gmtOffset;
  }
  $("pan_place").value = loc.display;
  $("pan_locationResults").innerHTML =
    `<div class="loc-item"><strong>✓ ${esc(loc.display)}</strong> &nbsp;·&nbsp; Lat ${esc(loc.lat)}, Lng ${esc(loc.lng)}, TZ ${esc(loc.gmtOffset ?? "—")}</div>`;
}

function qualityBadge(q) {
  const cls = { excellent: "badge-excellent", good: "badge-good", neutral: "badge-neutral", bad: "badge-bad", inauspicious: "badge-bad", auspicious: "badge-good" };
  return `<span class="badge ${cls[q] || "badge-neutral"}">${esc(q)}</span>`;
}

function timeRange(w) {
  return `<span class="time-range">${esc(w.start)} – ${esc(w.end)}</span>`;
}

function renderTithiCell(tithis) {
  if (tithis.length === 1) {
    const t = tithis[0];
    return `
      <div class="pan-element">
        <div class="pan-element-label">Tithi</div>
        <div class="pan-element-value">${esc(t.name)}</div>
        <div class="pan-element-sub">${esc(t.paksha)} Paksha · ${t.number}</div>
      </div>`;
  }
  // Two tithis — show transition
  const t1 = tithis[0], t2 = tithis[1];
  return `
    <div class="pan-element pan-element-transition">
      <div class="pan-element-label">Tithi</div>
      <div class="pan-element-value">${esc(t1.name)}</div>
      <div class="pan-element-sub">${esc(t1.paksha)} Paksha · ${t1.number}</div>
      <div class="pan-transition-tag">upto ${esc(t1.upto)}</div>
      <div class="pan-transition-divider"></div>
      <div class="pan-element-value">${esc(t2.name)}</div>
      <div class="pan-element-sub">${esc(t2.paksha)} Paksha · ${t2.number}</div>
      <div class="pan-transition-tag">from ${esc(t2.from)}</div>
    </div>`;
}

function renderNakCell(nakshatras) {
  if (nakshatras.length === 1) {
    const n = nakshatras[0];
    return `
      <div class="pan-element">
        <div class="pan-element-label">Nakshatra</div>
        <div class="pan-element-value">${esc(n.name)}</div>
        <div class="pan-element-sub">Pada ${n.pada} · Lord: ${esc(n.lord)}</div>
      </div>`;
  }
  const n1 = nakshatras[0], n2 = nakshatras[1];
  return `
    <div class="pan-element pan-element-transition">
      <div class="pan-element-label">Nakshatra</div>
      <div class="pan-element-value">${esc(n1.name)}</div>
      <div class="pan-element-sub">Pada ${n1.pada} · Lord: ${esc(n1.lord)}</div>
      <div class="pan-transition-tag">upto ${esc(n1.upto)}</div>
      <div class="pan-transition-divider"></div>
      <div class="pan-element-value">${esc(n2.name)}</div>
      <div class="pan-element-sub">Pada ${n2.pada} · Lord: ${esc(n2.lord)}</div>
      <div class="pan-transition-tag">from ${esc(n2.from)}</div>
    </div>`;
}

function renderKaranaCell(karanas) {
  if (karanas.length === 1) {
    return `
      <div class="pan-element">
        <div class="pan-element-label">Karana</div>
        <div class="pan-element-value">${esc(karanas[0].name)}</div>
        <div class="pan-element-sub">&nbsp;</div>
      </div>`;
  }
  // Multiple karanas — show each with timing, separated by dashed dividers
  const rows = karanas.map((k, i) => {
    const timing = k.from
      ? `<div class="pan-transition-tag">from ${esc(k.from)}${k.upto ? " · upto " + esc(k.upto) : ""}</div>`
      : (k.upto ? `<div class="pan-transition-tag">upto ${esc(k.upto)}</div>` : "");
    return (i > 0 ? '<div class="pan-transition-divider"></div>' : "") +
      `<div class="pan-element-value">${esc(k.name)}</div>${timing}`;
  }).join("");
  return `
    <div class="pan-element pan-element-transition">
      <div class="pan-element-label">Karana</div>
      ${rows}
    </div>`;
}

function renderPanchang(data) {
  const p = data.panchang;
  const ina = data.inauspicious;

  $("pan_summary").innerHTML = `
    <h2>Panchang — ${esc(data.date)}${data.place ? " · " + esc(data.place) : ""}</h2>

    <h3 class="pan-section-title">Pancha Anga — Five Sacred Elements</h3>
    <div class="pan-grid">
      ${renderTithiCell(p.tithis)}
      ${renderNakCell(p.nakshatras)}
      <div class="pan-element">
        <div class="pan-element-label">Yoga</div>
        <div class="pan-element-value">${esc(p.yoga.name)}</div>
        <div class="pan-element-sub">${qualityBadge(p.yoga.quality)}</div>
      </div>
      ${renderKaranaCell(p.karanas)}
      <div class="pan-element">
        <div class="pan-element-label">Vara</div>
        <div class="pan-element-value">${esc(p.vara.name)}</div>
        <div class="pan-element-sub">${esc(p.vara.hindi)} · Lord: ${esc(p.vara.lord)}</div>
      </div>
    </div>

    <h3 class="pan-section-title">Auspicious Timing</h3>
    <div class="pan-timing-grid">
      <div class="pan-timing good">
        <div class="pan-timing-label">Abhijit Muhurat</div>
        <div class="pan-timing-desc">Most auspicious window of the day</div>
        <div class="pan-timing-time">${timeRange(data.abhijit_muhurat)}</div>
      </div>
    </div>

    <h3 class="pan-section-title">Inauspicious Periods — Avoid for New Beginnings</h3>
    <div class="pan-timing-grid">
      <div class="pan-timing bad">
        <div class="pan-timing-label">Rahu Kaal</div>
        <div class="pan-timing-desc">Ruled by Rahu — avoid important work</div>
        <div class="pan-timing-time">${timeRange(ina.rahu_kaal)}</div>
      </div>
      <div class="pan-timing bad">
        <div class="pan-timing-label">Yamgandam</div>
        <div class="pan-timing-desc">Inauspicious — avoid travel and new starts</div>
        <div class="pan-timing-time">${timeRange(ina.yamgandam)}</div>
      </div>
      <div class="pan-timing bad">
        <div class="pan-timing-label">Gulikai</div>
        <div class="pan-timing-desc">Ruled by Saturn — avoid financial matters</div>
        <div class="pan-timing-time">${timeRange(ina.gulikai)}</div>
      </div>
    </div>

    <h3 class="pan-section-title">Choghadiya — Day Periods</h3>
    ${choTable(data.choghadiya.day)}

    <h3 class="pan-section-title">Choghadiya — Night Periods</h3>
    ${choTable(data.choghadiya.night)}
  `;
}

function choTable(slots) {
  const rows = slots.map(s => `
    <tr class="cho-row-${s.quality}">
      <td><strong>${esc(s.name)}</strong></td>
      <td>${qualityBadge(s.quality)}</td>
      <td>${esc(s.start)} – ${esc(s.end)}</td>
      <td class="cho-meaning">${esc(s.meaning)}</td>
    </tr>`).join("");
  return `
    <table class="table cho-table">
      <thead><tr><th>Choghadiya</th><th>Quality</th><th>Time</th><th>Guidance</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}

async function submitPanchang(e) {
  e.preventDefault();

  const payload = {
    date: $("pan_date").value,
    latitude: parseFloat($("pan_latitude").value),
    longitude: parseFloat($("pan_longitude").value),
    timezone_offset_hours: parseFloat($("pan_timezone").value),
    place: $("pan_place").value,
  };

  $("pan_summary").innerHTML = `
    <div class="loading-state">
      <div class="spinner"></div>
      <p class="loading-text">Calculating Panchang…</p>
      <p class="loading-sub">Reading planetary positions</p>
    </div>`;

  try {
    const res = await fetch("/api/panchang", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      $("pan_summary").innerHTML = `
        <div style="padding:20px;text-align:center">
          <p style="color:#9a3412;font-weight:700;font-size:16px;margin:0 0 8px">Unable to calculate Panchang</p>
          <p style="color:#78716c;font-size:14px;margin:0">${esc(err.detail || "Please check all fields and try again.")}</p>
        </div>`;
      return;
    }

    const data = await res.json();
    renderPanchang(data);

    document.querySelectorAll(".results .card").forEach(el => {
      el.classList.remove("fade-in");
      void el.offsetWidth;
      el.classList.add("fade-in");
    });
  } catch (err) {
    $("pan_summary").innerHTML = `<div style="padding:20px;text-align:center"><p style="color:#9a3412">An error occurred. Please try again.</p></div>`;
  }
}

$("pan_searchLocation").addEventListener("click", searchLocation);
$("panchangForm").addEventListener("submit", submitPanchang);
