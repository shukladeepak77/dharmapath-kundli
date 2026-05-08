(function () {
  const WELCOME_HTML = `Namaste 🙏 I am Jyotishi, your Vedic astrology guide.<br><br>For a personal reading (Dasha, Sade Sati, career, marriage, etc.), <a class="chat-inline-link" id="nudge-open-panel">click here to enter your birth details</a> — I'll interpret your actual chart calculated with Lahiri Ayanamsha.<br><br>For general Jyotish questions, just ask!`;

  const DISCLAIMER = "⚠ Important: Jyotisha offers guidance rooted in ancient wisdom, not certainty. These insights are based on planetary positions at the time of your birth and are intended for self-reflection and spiritual guidance only — not as a substitute for professional advice in medical, legal, financial, or personal matters. For important life decisions, please consult a qualified Jyotishi in person. Dharma Path USA Foundation offers this as seva.";

  let history = [];
  let kundliContext = "";
  let chartLabel = "";
  let disclaimerShown = false;
  let busy = false;

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function buildNudge() {
    const nudge = document.createElement("div");
    nudge.id = "chatbot-nudge";
    nudge.innerHTML = "🪔 <strong>Ask Jyotishi</strong><br><span style='color:#78716c;font-size:12px'>Your Vedic astrology guide</span>";
    document.body.appendChild(nudge);

    function dismiss() {
      nudge.classList.add("hide");
      setTimeout(() => nudge.remove(), 280);
    }

    nudge.addEventListener("click", () => { dismiss(); openChat(); });
    setTimeout(dismiss, 6000);
  }

  function buildWidget() {
    document.body.insertAdjacentHTML("beforeend", `
      <button id="chatbot-btn" title="Ask Jyotishi">🔮</button>

      <div id="chatbot-window">
        <div class="chatbot-header">
          <span class="chatbot-header-icon">🪔</span>
          <div class="chatbot-header-info">
            <p class="chatbot-header-name">Jyotishi</p>
            <p class="chatbot-header-sub">Vedic Astrology Guide</p>
          </div>
          <button id="chatbot-chart-btn" title="Calculate birth chart">📊</button>
          <button id="chatbot-close" title="Close">✕</button>
        </div>

        <!-- Birth chart panel (hidden by default) -->
        <div id="chatbot-birth-panel">
          <p class="cb-panel-title">📊 Calculate My Chart</p>
          <div class="cb-field">
            <label>Date of Birth</label>
            <input type="date" id="cb_date" />
          </div>
          <div class="cb-field">
            <label>Time of Birth</label>
            <input type="time" id="cb_time" value="12:00" />
          </div>
          <div class="cb-field">
            <label>Place of Birth</label>
            <input type="text" id="cb_location" placeholder="e.g. Delhi, India" />
          </div>
          <div id="cb_loc_result"></div>
          <button id="cb_calculate">Calculate &amp; Load Chart</button>
        </div>

        <!-- Chart loaded badge (hidden until chart computed) -->
        <div id="chatbot-chart-badge" style="display:none" class="chatbot-chart-badge">
          <span id="chatbot-chart-label">✓ Chart loaded</span>
          <button id="chatbot-chart-btn2" title="Change chart">Change</button>
        </div>

        <div id="chatbot-messages"></div>

        <div class="chatbot-input-row">
          <textarea id="chatbot-input" placeholder="Ask about your Kundli, Dasha, Milan…" rows="1"></textarea>
          <button id="chatbot-send" title="Send">➤</button>
        </div>
      </div>
    `);

    document.getElementById("chatbot-btn").addEventListener("click", openChat);
    document.getElementById("chatbot-close").addEventListener("click", closeChat);
    document.getElementById("chatbot-chart-btn").addEventListener("click", toggleBirthPanel);
    document.getElementById("chatbot-chart-btn2").addEventListener("click", toggleBirthPanel);
    document.getElementById("cb_calculate").addEventListener("click", calculateChart);
    document.getElementById("chatbot-send").addEventListener("click", sendMessage);
    document.getElementById("chatbot-input").addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
  }

  function openChat() {
    document.getElementById("chatbot-window").classList.add("open");
    if (history.length === 0) appendWelcomeMsg();
    setTimeout(() => document.getElementById("chatbot-input").focus(), 220);
  }

  function closeChat() {
    document.getElementById("chatbot-window").classList.remove("open");
  }

  function toggleBirthPanel() {
    const panel = document.getElementById("chatbot-birth-panel");
    panel.classList.toggle("visible");
    if (panel.classList.contains("visible")) {
      document.getElementById("cb_location").focus();
    }
  }

  // ── Chart calculation ───────────────────────────────────────────────────

  async function calculateChart() {
    const date = document.getElementById("cb_date").value;
    const time = document.getElementById("cb_time").value;
    const locInput = document.getElementById("cb_location").value.trim();
    const locResult = document.getElementById("cb_loc_result");
    const btn = document.getElementById("cb_calculate");

    if (!date || !time || !locInput) {
      locResult.textContent = "Please fill in all three fields.";
      locResult.style.color = "#9a3412";
      return;
    }

    btn.disabled = true;
    btn.textContent = "Searching location…";
    locResult.textContent = "";
    locResult.style.color = "#059669";

    let lat, lng, tz, place;
    try {
      const res = await fetch(`/api/location-search?q=${encodeURIComponent(locInput)}`);
      const data = await res.json();
      if (!data.results || data.results.length === 0) {
        locResult.textContent = "Location not found. Try a different city name.";
        locResult.style.color = "#9a3412";
        btn.disabled = false;
        btn.textContent = "Calculate & Load Chart";
        return;
      }
      const loc = data.results[0];
      lat = loc.lat; lng = loc.lng; tz = loc.gmtOffset; place = loc.display;
      locResult.textContent = `✓ ${place}`;
    } catch (_) {
      locResult.textContent = "Location search failed. Try again.";
      locResult.style.color = "#9a3412";
      btn.disabled = false;
      btn.textContent = "Calculate & Load Chart";
      return;
    }

    btn.textContent = "Calculating chart…";

    try {
      const res = await fetch("/api/generate-kundli", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          birth_date: date,
          birth_time: time,
          place: place,
          latitude: lat,
          longitude: lng,
          timezone_offset_hours: tz,
        }),
      });
      if (!res.ok) {
        locResult.textContent = "Chart calculation failed. Check birth details.";
        locResult.style.color = "#9a3412";
        return;
      }
      const chart = await res.json();
      kundliContext = formatKundliContext(chart, place, date, time);
      chartLabel = `${date} · ${time} · ${place.split(",")[0]}`;

      document.getElementById("chatbot-birth-panel").classList.remove("visible");
      document.getElementById("chatbot-chart-badge").style.display = "flex";
      document.getElementById("chatbot-chart-label").textContent = `✓ Chart: ${chartLabel}`;

      const confirmMsg = `I've loaded your birth chart (${chartLabel}) calculated with Lahiri Ayanamsha. Now ask me anything — your Lagna, current Dasha, Sade Sati, or any other question about your chart!`;
      appendBotMsg(confirmMsg);
      history.push({ role: "assistant", content: confirmMsg });

    } catch (_) {
      locResult.textContent = "An error occurred. Please try again.";
      locResult.style.color = "#9a3412";
    } finally {
      btn.disabled = false;
      btn.textContent = "Calculate & Load Chart";
    }
  }

  function formatKundliContext(data, place, date, time) {
    const positions = data.d1_rashi_chart;
    const dashas = data.vimshottari_mahadasha;
    const bd = data.birth_data || {};

    const order = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
    const planetLines = order.map(p => {
      const x = positions[p];
      if (!x) return null;
      const retro = x.retrograde && !["Lagna", "Rahu", "Ketu"].includes(p) ? " [Retrograde]" : "";
      return `  ${p}: ${x.rashi} | House ${x.house} | ${x.nakshatra} Pada ${x.pada}${retro}`;
    }).filter(Boolean).join("\n");

    const today = new Date().toISOString().slice(0, 10);
    let dashaLines = "";
    for (const maha of dashas) {
      const isCurrent = maha.start <= today && today <= maha.end;
      if (isCurrent) {
        const currentAntar = (maha.antardashas || []).find(a => a.start <= today && today <= a.end);
        dashaLines += `  Current Mahadasha: ${maha.lord} (${maha.start} to ${maha.end})\n`;
        if (currentAntar) {
          dashaLines += `  Current Antardasha: ${currentAntar.lord} (${currentAntar.start} to ${currentAntar.end})\n`;
        }
      }
    }
    dashaLines += `  All Mahadashas: ${dashas.map(d => `${d.lord} (${d.start}–${d.end})`).join(", ")}`;

    return `BIRTH CHART DATA — Calculated with Lahiri Ayanamsha (Vedic Sidereal)
Birth Date: ${date} | Time: ${time} | Place: ${place}

PLANETARY POSITIONS (D1 Rashi Chart):
${planetLines}

VIMSHOTTARI DASHA:
${dashaLines}`;
  }

  // ── Chat messaging ──────────────────────────────────────────────────────

  function appendWelcomeMsg() {
    const el = document.createElement("div");
    el.className = "chat-msg bot";
    el.innerHTML = WELCOME_HTML;
    appendMsg(el);
    const link = document.getElementById("nudge-open-panel");
    if (link) link.addEventListener("click", toggleBirthPanel);
  }

  function appendDisclaimerMsg(text) {
    const el = document.createElement("div");
    el.className = "chat-msg disclaimer";
    el.textContent = text;
    appendMsg(el);
  }

  function appendBotMsg(text) {
    const el = document.createElement("div");
    el.className = "chat-msg bot";
    el.textContent = text;
    appendMsg(el);
    return el;
  }

  function appendUserMsg(text) {
    const el = document.createElement("div");
    el.className = "chat-msg user";
    el.textContent = text;
    appendMsg(el);
  }

  function appendTyping() {
    const el = document.createElement("div");
    el.className = "chat-msg typing";
    el.id = "chatbot-typing";
    el.textContent = "Jyotishi is thinking…";
    appendMsg(el);
    return el;
  }

  function appendMsg(el) {
    const box = document.getElementById("chatbot-messages");
    box.appendChild(el);
    box.scrollTop = box.scrollHeight;
  }

  async function sendMessage() {
    if (busy) return;
    const input = document.getElementById("chatbot-input");
    const text = input.value.trim();
    if (!text) return;

    input.value = "";
    appendUserMsg(text);
    history.push({ role: "user", content: text });

    if (kundliContext && !disclaimerShown) {
      appendDisclaimerMsg(DISCLAIMER);
      disclaimerShown = true;
    }

    busy = true;
    document.getElementById("chatbot-send").disabled = true;
    const typing = appendTyping();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: history,
          kundli_context: kundliContext,
        }),
      });

      typing.remove();

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        appendBotMsg(err.detail || "Sorry, I encountered an error. Please try again.");
        history.pop();
        return;
      }

      const data = await res.json();
      const reply = data.reply || "I'm sorry, I couldn't generate a response.";
      appendBotMsg(reply);
      history.push({ role: "assistant", content: reply });

      if (history.length > 40) history = history.slice(-40);
    } catch (_) {
      typing.remove();
      appendBotMsg("Network error. Please check your connection and try again.");
      history.pop();
    } finally {
      busy = false;
      document.getElementById("chatbot-send").disabled = false;
      document.getElementById("chatbot-input").focus();
    }
  }

  function init() {
    buildWidget();
    setTimeout(buildNudge, 1500);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
