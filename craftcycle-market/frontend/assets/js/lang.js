/**
 * frontend/js/lang.js
 * ────────────────────────────────────────────────────────────
 * Multi-language support for CraftCycle Market.
 * Uses Google Translate Element (free, no API key needed).
 * Supports English + 12 major Indian languages.
 *
 * Include AFTER config.js:
 *   <script src="js/lang.js"></script>
 */

(function () {
  // ── Language definitions ────────────────────────────────
  const LANGUAGES = [
    { code: "", name: "English", native: "English", flag: "🇬🇧" },
    { code: "hi", name: "Hindi", native: "हिंदी", flag: "🇮🇳" },
    { code: "bn", name: "Bengali", native: "বাংলা", flag: "🇮🇳" },
    { code: "te", name: "Telugu", native: "తెలుగు", flag: "🇮🇳" },
    { code: "ta", name: "Tamil", native: "தமிழ்", flag: "🇮🇳" },
    { code: "kn", name: "Kannada", native: "ಕನ್ನಡ", flag: "🇮🇳" }
  ];

  const STORAGE_KEY = "cc_lang";

  // ── Inject CSS ──────────────────────────────────────────
  const style = document.createElement("style");
  style.textContent = `
    /* Hide default Google Translate bar and prevent Body Shift */
    .goog-te-banner-frame { display: none !important; }
    .skiptranslate { display: none !important; }
    .skiptranslate.goog-te-gadget { display: none !important; }
    body, html { top: 0 !important; position: static !important; }
    
    /* Hide Google Translate Tooltips and Artifacts */
    .goog-tooltip { display: none !important; }
    .goog-tooltip:hover { display: none !important; }
    .goog-text-highlight { background-color: transparent !important; border: none !important; box-shadow: none !important; }
    #goog-gt-tt { display: none !important; }
    
    /* ── Language Picker ── */
    #lang-picker-btn {
      display: flex; align-items: center; gap: 6px;
      padding: 6px 12px; border-radius: var(--r-full);
      background: var(--surface-2); border: 1px solid var(--border);
      color: var(--text-2); font-size: 0.8rem; font-weight: 600;
      cursor: pointer; transition: all 0.15s; position: relative;
      font-family: var(--font-body);
      white-space: nowrap;
    }
    #lang-picker-btn:hover { border-color: var(--green); color: var(--green); }

    #lang-dropdown {
      position: absolute; top: calc(100% + 8px); right: 0;
      width: 220px; max-width: calc(100vw - 32px); background: var(--surface-1);
      border: 1px solid rgba(0,212,255,0.2);
      border-radius: var(--r-xl); padding: var(--s2);
      box-shadow: 0 12px 40px rgba(0,0,0,0.6);
      z-index: 10000;
      display: none; flex-direction: column; gap: 2px;
      max-height: 360px; overflow-y: auto;
    }
    #lang-dropdown.open { display: flex; animation: fadeIn 0.15s ease; }
    #lang-dropdown::-webkit-scrollbar { width: 4px; }
    #lang-dropdown::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.2); border-radius: 2px; }

    .lang-option {
      display: flex; align-items: center; gap: 10px;
      padding: 9px 12px; border-radius: var(--r-md);
      cursor: pointer; transition: background 0.1s;
      border: none; background: none; width: 100%; text-align: left;
      color: var(--text-2); font-family: var(--font-body);
    }
    .lang-option:hover { background: var(--surface-3); color: var(--text-1); }
    .lang-option.active { background: var(--green-glow); color: var(--green); }
    .lang-option-flag { font-size: 1.1rem; flex-shrink: 0; }
    .lang-option-names { display: flex; flex-direction: column; }
    .lang-option-native { font-size: 0.875rem; font-weight: 700; }
    .lang-option-english { font-size: 0.7rem; color: var(--text-3); }
    .lang-option.active .lang-option-english { color: var(--green); opacity: 0.7; }

    .lang-section-label {
      font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.1em; color: var(--text-3); padding: 8px 12px 4px;
    }

    /* Container for the button */
    #lang-picker-wrap { position: relative; }
  `;
  document.head.appendChild(style);

  // ── Inject hidden Google Translate element ──────────────
  const gtDiv = document.createElement("div");
  gtDiv.id = "google_translate_element";
  gtDiv.style.cssText = "position:absolute;top:-9999px;visibility:hidden;";
  document.body.appendChild(gtDiv);

  // ── Google Translate init callback ──────────────────────
  window.googleTranslateElementInit = function () {
    new google.translate.TranslateElement({
      pageLanguage: "en",
      includedLanguages: "hi,bn,te,ta,kn",
      autoDisplay: false,
      multilanguagePage: true,
    }, "google_translate_element");

    // Restore saved language
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      setTimeout(() => applyLanguage(saved), 800);
    }
  };

  // ── Load Google Translate script ────────────────────────
  const script = document.createElement("script");
  script.src = "//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
  script.async = true;
  document.head.appendChild(script);

  // ── Apply language ───────────────────────────────────────
  function applyLanguage(code) {
    if (!code) {
      // Restore English — reset Google Translate
      const frame = document.querySelector(".goog-te-banner-frame");
      const restore = frame?.contentDocument?.querySelector("#:0.restore");
      if (restore) { restore.click(); return; }

      // Cookie method
      document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
      document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=" + window.location.hostname;
      location.reload();
      return;
    }

    // Set via Google Translate select
    const sel = document.querySelector(".goog-te-combo");
    if (sel) {
      sel.value = code;
      sel.dispatchEvent(new Event("change"));
      localStorage.setItem(STORAGE_KEY, code);
    } else {
      // Fallback: cookie method
      document.cookie = `googtrans=/en/${code}`;
      document.cookie = `googtrans=/en/${code}; domain=${window.location.hostname}`;
      location.reload();
    }
  }

  // ── Build picker widget ──────────────────────────────────
  function buildPicker() {
    const current = localStorage.getItem(STORAGE_KEY) || "";
    const currentLang = LANGUAGES.find(l => l.code === current) || LANGUAGES[0];

    const wrap = document.createElement("div");
    wrap.id = "lang-picker-wrap";
    wrap.className = "notranslate";

    wrap.innerHTML = `
      <button id="lang-picker-btn" onclick="window.__toggleLangDropdown()">
        <span>${currentLang.flag}</span>
        <span class="lang-current-name">${currentLang.native}</span>
        <span>▾</span>
      </button>
      <div id="lang-dropdown">
        <div class="lang-section-label">🌐 Choose Language</div>
        ${LANGUAGES.map(l => `
          <button class="lang-option ${l.code === current ? "active" : ""}"
                  onclick="window.__setLang('${l.code}')">
            <span class="lang-option-flag">${l.flag}</span>
            <span class="lang-option-names">
              <span class="lang-option-native">${l.native}</span>
              <span class="lang-option-english">${l.name}</span>
            </span>
            ${l.code === current ? '<span style="margin-left:auto;color:var(--green);font-size:0.8rem">✓</span>' : ""}
          </button>
        `).join("")}
      </div>
    `;

    return wrap;
  }

  // ── Global handlers ──────────────────────────────────────
  window.__toggleLangDropdown = function () {
    const dd = document.getElementById("lang-dropdown");
    if (dd) dd.classList.toggle("open");
  };

  window.__setLang = function (code) {
    const dd = document.getElementById("lang-dropdown");
    if (dd) dd.classList.remove("open");
    localStorage.setItem(STORAGE_KEY, code);
    applyLanguage(code);
    // Update button label immediately
    const lang = LANGUAGES.find(l => l.code === code) || LANGUAGES[0];
    const btn = document.getElementById("lang-picker-btn");
    if (btn) {
      btn.innerHTML = `<span>${lang.flag}</span><span class="lang-current-name">${lang.native}</span><span>▾</span>`;
    }
  };

  // Auto-apply user preference and prevent emoji translation
  document.addEventListener("DOMContentLoaded", () => {
    // Prevent Google Translate from translating emojis by adding 'notranslate'
    const iconSelectors = [
      '.navbar-logo-icon', '.cat-icon', '.feature-icon', '.hiw-num', 
      '.testimonial-avatar', '.logo-icon', '.nav-icon', '.upload-icon', 
      '.social-btn', '.notif-btn', '.user-avatar', '.map-ctrl-btn', 
      '.wishlist-btn', '.stat-icon', '.popup-btn'
    ];
    iconSelectors.forEach(selector => {
      document.querySelectorAll(selector).forEach(el => el.classList.add('notranslate'));
    });
  });

  // Close dropdown when clicking outside
  document.addEventListener("click", function (e) {
    const wrap = document.getElementById("lang-picker-wrap");
    if (wrap && !wrap.contains(e.target)) {
      const dd = document.getElementById("lang-dropdown");
      if (dd) dd.classList.remove("open");
    }
  });

  // ── Inject picker into topbar ────────────────────────────
  function injectPicker() {
    // Case 1: landing page pre-placed the wrapper — just fill it
    const existing = document.getElementById("lang-picker-wrap");
    if (existing) {
      existing.classList.add("notranslate"); // Add class to existing wrapper
      // Already populated
      if (existing.querySelector("#lang-picker-btn")) return;
      const picker = buildPicker();
      // Move picker's children into the existing wrapper
      while (picker.firstChild) existing.appendChild(picker.firstChild);
      return;
    }

    // Case 2: app page — inject before first child of .topbar-right
    const topbarRight = document.querySelector(".topbar-right");
    if (!topbarRight) return;

    const picker = buildPicker();
    topbarRight.insertBefore(picker, topbarRight.firstChild);
  }

  // Wait for DOM
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectPicker);
  } else {
    injectPicker();
  }

  // Also try after a short delay (for dynamic pages)
  setTimeout(injectPicker, 500);

})();
