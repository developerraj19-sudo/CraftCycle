/**
 * frontend/js/chatbot.js
 * ──────────────────────
 * CraftCycle AI Assistant — floating chatbot widget.
 * Powered by OpenAI GPT-4o.
 * Include this script on every page AFTER config.js, api.js, utils.js
 *
 * Usage: just include <script src="js/chatbot.js"></script>
 * The widget self-injects into the page.
 */

(function () {
  // ── Configuration ─────────────────────────────────────────
  const BOT_NAME = "CraftBot 🌿";
  const OPENAI_KEY = CONFIG.OPENAI_API_KEY || "";   // set in config.js
  const MODEL = "gpt-4o";
  const MAX_TOKENS = 500;

  const SYSTEM_PROMPT = `You are CraftBot, the friendly AI assistant for CraftCycle Market — a circular economy marketplace where users buy scrap materials, create upcycled products, and sell them.

Your personality: Helpful, encouraging, eco-conscious, and knowledgeable about upcycling, DIY crafts, and sustainable business.

You help users with:
- Finding the right scrap materials for their projects
- DIY product ideas and step-by-step guidance
- Pricing and selling strategies on the marketplace
- Green Coins and rewards system
- Platform navigation and features
- Eco-impact calculations and sustainability tips

Keep responses concise (2-4 sentences max unless asked for detail). Use occasional emojis to stay friendly. Always encourage sustainable practices.

If asked something outside CraftCycle (politics, unrelated topics), politely redirect to platform topics.`;

  const QUICK_PROMPTS = [
    "💡 Product ideas from plastic bottles",
    "🏪 How to list scrap materials?",
    "🪙 How do Green Coins work?",
    "🔍 What does the AI Scanner do?",
    "📦 Best selling upcycled products",
  ];

  // ── State ─────────────────────────────────────────────────
  let isOpen = false;
  let isTyping = false;
  let conversation = [];   // { role, content }[]

  // ── Inject CSS ────────────────────────────────────────────
  const style = document.createElement("style");
  style.textContent = `
    /* ── Chatbot Widget ── */
    #cb-toggle {
      position: fixed; bottom: 28px; right: 28px; z-index: 9000;
      width: 58px; height: 58px; border-radius: 50%;
      background: linear-gradient(135deg, #00FF88, #00D4FF);
      border: none; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.6rem;
      box-shadow: 0 4px 20px rgba(0,255,136,0.5);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    #cb-toggle:hover { transform: scale(1.1); box-shadow: 0 6px 28px rgba(0,255,136,0.7); }
    #cb-toggle.open  { background: linear-gradient(135deg, #FF4D4D, #F97316); }

    #cb-unread {
      position: absolute; top: -4px; right: -4px;
      width: 20px; height: 20px; border-radius: 50%;
      background: #FF4D4D; color: #fff;
      font-size: 0.65rem; font-weight: 700;
      display: flex; align-items: center; justify-content: center;
      border: 2px solid #050D1A;
      animation: cb-pulse 2s infinite;
      display: none;
    }
    @keyframes cb-pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.2)} }

    #cb-panel {
      position: fixed; bottom: 100px; right: 28px; z-index: 8999;
      width: 370px; height: 540px;
      background: #0A1628;
      border: 1px solid rgba(0,212,255,0.2);
      border-radius: 20px;
      display: flex; flex-direction: column;
      box-shadow: 0 12px 50px rgba(0,0,0,0.7), 0 0 0 1px rgba(0,255,136,0.1);
      transform: scale(0.85) translateY(20px);
      opacity: 0; pointer-events: none;
      transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
      overflow: hidden;
    }
    #cb-panel.open {
      transform: scale(1) translateY(0);
      opacity: 1; pointer-events: all;
    }

    /* Header */
    #cb-header {
      padding: 16px 18px;
      background: linear-gradient(135deg, rgba(0,255,136,0.12), rgba(0,212,255,0.08));
      border-bottom: 1px solid rgba(0,212,255,0.15);
      display: flex; align-items: center; justify-content: space-between;
      flex-shrink: 0;
    }
    .cb-avatar {
      width: 38px; height: 38px; border-radius: 50%;
      background: linear-gradient(135deg, #00FF88, #00D4FF);
      display: flex; align-items: center; justify-content: center;
      font-size: 1.2rem; flex-shrink: 0;
    }
    .cb-header-info { flex: 1; margin-left: 12px; }
    .cb-bot-name { font-family: 'Orbitron', monospace; font-size: 0.82rem; font-weight: 700; color: #00FF88; }
    .cb-status {
      font-size: 0.7rem; color: #4A9060; display: flex; align-items: center; gap: 5px; margin-top: 2px;
    }
    .cb-status-dot {
      width: 7px; height: 7px; border-radius: 50%; background: #00FF88;
      animation: cb-pulse 2s infinite;
    }
    #cb-close {
      background: none; border: none; cursor: pointer;
      color: #4A6080; font-size: 1.1rem; padding: 4px; border-radius: 6px;
      transition: color 0.15s;
    }
    #cb-close:hover { color: #E8F4FF; }

    /* Messages */
    #cb-messages {
      flex: 1; overflow-y: auto; padding: 16px;
      display: flex; flex-direction: column; gap: 12px;
      scroll-behavior: smooth;
    }
    #cb-messages::-webkit-scrollbar { width: 4px; }
    #cb-messages::-webkit-scrollbar-track { background: transparent; }
    #cb-messages::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.2); border-radius: 2px; }

    .cb-msg {
      display: flex; gap: 8px; align-items: flex-end;
      animation: cb-fadein 0.2s ease;
    }
    @keyframes cb-fadein { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }

    .cb-msg.user { flex-direction: row-reverse; }

    .cb-bubble {
      max-width: 78%; padding: 10px 14px;
      border-radius: 16px; font-size: 0.84rem; line-height: 1.55;
    }
    .cb-msg.bot  .cb-bubble {
      background: #111B2E; border: 1px solid rgba(0,212,255,0.15);
      color: #C8DCF0; border-radius: 4px 16px 16px 16px;
    }
    .cb-msg.user .cb-bubble {
      background: linear-gradient(135deg, #00FF88, #00D4FF);
      color: #050D1A; font-weight: 600;
      border-radius: 16px 4px 16px 16px;
    }
    .cb-msg-avatar {
      width: 28px; height: 28px; border-radius: 50%;
      background: linear-gradient(135deg, #00FF88, #00D4FF);
      display: flex; align-items: center; justify-content: center;
      font-size: 0.9rem; flex-shrink: 0;
    }
    .cb-msg.user .cb-msg-avatar { background: #1A2740; border: 1px solid rgba(0,255,136,0.3); }

    /* Timestamp */
    .cb-time {
      font-size: 0.65rem; color: #2A4060; text-align: center;
      margin: 4px 0;
    }

    /* Typing indicator */
    .cb-typing {
      display: flex; gap: 5px; padding: 12px 16px;
      background: #111B2E; border: 1px solid rgba(0,212,255,0.15);
      border-radius: 4px 16px 16px 16px; max-width: 70px;
    }
    .cb-typing span {
      width: 6px; height: 6px; border-radius: 50%;
      background: #00D4FF; animation: cb-bounce 1.2s infinite;
    }
    .cb-typing span:nth-child(2) { animation-delay: 0.15s; }
    .cb-typing span:nth-child(3) { animation-delay: 0.30s; }
    @keyframes cb-bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-6px)} }

    /* Quick prompts */
    #cb-quick {
      padding: 8px 14px 0;
      display: flex; flex-wrap: wrap; gap: 6px;
      flex-shrink: 0;
    }
    .cb-quick-btn {
      padding: 5px 10px; border-radius: 999px;
      background: rgba(0,212,255,0.08); border: 1px solid rgba(0,212,255,0.2);
      color: #7ABFDA; font-size: 0.72rem; cursor: pointer;
      transition: all 0.15s; white-space: nowrap;
    }
    .cb-quick-btn:hover { background: rgba(0,255,136,0.12); border-color: rgba(0,255,136,0.3); color: #00FF88; }

    /* Input area */
    #cb-input-area {
      padding: 12px 14px 14px;
      border-top: 1px solid rgba(0,212,255,0.12);
      display: flex; gap: 8px; align-items: flex-end;
      flex-shrink: 0;
    }
    #cb-input {
      flex: 1; background: #111B2E; border: 1px solid rgba(0,212,255,0.2);
      border-radius: 12px; color: #E8F4FF; font-size: 0.875rem;
      padding: 10px 14px; resize: none; outline: none; max-height: 100px;
      font-family: 'DM Sans', sans-serif; line-height: 1.5;
      transition: border-color 0.15s;
    }
    #cb-input:focus { border-color: rgba(0,255,136,0.4); }
    #cb-input::placeholder { color: #2A4060; }
    #cb-send {
      width: 40px; height: 40px; border-radius: 12px; flex-shrink: 0;
      background: linear-gradient(135deg, #00FF88, #00D4FF);
      border: none; cursor: pointer; font-size: 1rem;
      display: flex; align-items: center; justify-content: center;
      transition: opacity 0.15s, transform 0.15s;
    }
    #cb-send:hover { opacity: 0.85; transform: scale(1.05); }
    #cb-send:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

    /* Clear btn */
    #cb-clear {
      background: none; border: none; cursor: pointer;
      font-size: 0.72rem; color: #2A4060; padding: 4px 8px;
      border-radius: 6px; transition: color 0.15s;
    }
    #cb-clear:hover { color: #FF4D4D; }

    /* No API key warning */
    #cb-no-key {
      margin: 10px 14px; padding: 10px 14px;
      background: rgba(249,115,22,0.1); border: 1px solid rgba(249,115,22,0.3);
      border-radius: 10px; font-size: 0.78rem; color: #F97316;
      display: none;
    }

    /* Mobile */
    @media (max-width: 480px) {
      #cb-panel { width: calc(100vw - 32px); right: 16px; bottom: 90px; }
      #cb-toggle { right: 16px; bottom: 16px; }
    }
  `;
  document.head.appendChild(style);

  // ── Inject HTML ───────────────────────────────────────────
  const container = document.createElement("div");
  container.id = "craftbot-container";
  container.innerHTML = `
    <!-- Toggle button -->
    <button id="cb-toggle" title="Chat with CraftBot" class="notranslate">♻️<span id="cb-unread"></span></button>

    <!-- Chat panel -->
    <div id="cb-panel">
      <!-- Header -->
      <div id="cb-header">
        <div class="cb-avatar notranslate">🤖</div>
        <div class="cb-header-info">
          <div class="cb-bot-name">${BOT_NAME}</div>
          <div class="cb-status">
            <div class="cb-status-dot"></div>
            <span id="cb-status-text">Online — Ask me anything!</span>
          </div>
        </div>
        <button id="cb-clear" title="Clear chat">🗑️</button>
        <button id="cb-close" title="Close">✕</button>
      </div>

      <!-- No API key warning -->
      <div id="cb-no-key">
        ⚠️ OpenAI API key not configured. Set <code>OPENAI_API_KEY</code> in <code>js/config.js</code>.
      </div>

      <!-- Messages -->
      <div id="cb-messages"></div>

      <!-- Quick prompts -->
      <div id="cb-quick"></div>

      <!-- Input -->
      <div id="cb-input-area">
        <textarea id="cb-input" rows="1" placeholder="Ask CraftBot anything…"
                  onkeydown="window._cbKeydown(event)"></textarea>
        <button id="cb-send" onclick="window._cbSend()">➤</button>
      </div>
    </div>
  `;
  document.body.appendChild(container);

  // ── DOM refs ──────────────────────────────────────────────
  const toggleBtn = document.getElementById("cb-toggle");
  const panel = document.getElementById("cb-panel");
  const messagesEl = document.getElementById("cb-messages");
  const inputEl = document.getElementById("cb-input");
  const sendBtn = document.getElementById("cb-send");
  const quickEl = document.getElementById("cb-quick");
  const unreadBadge = document.getElementById("cb-unread");
  const noKeyEl = document.getElementById("cb-no-key");
  const statusText = document.getElementById("cb-status-text");

  // ── Toggle panel ──────────────────────────────────────────
  function togglePanel() {
    isOpen = !isOpen;
    panel.classList.toggle("open", isOpen);
    toggleBtn.classList.toggle("open", isOpen);
    toggleBtn.textContent = isOpen ? "✕" : "♻️";
    if (isOpen) {
      unreadBadge.style.display = "none";
      if (conversation.length === 0) showWelcome();
      setTimeout(() => inputEl.focus(), 300);
    }
  }

  toggleBtn.addEventListener("click", togglePanel);
  document.getElementById("cb-close").addEventListener("click", togglePanel);

  // Clear chat
  document.getElementById("cb-clear").addEventListener("click", () => {
    conversation = [];
    messagesEl.innerHTML = "";
    showWelcome();
  });

  // ── Welcome message ───────────────────────────────────────
  function showWelcome() {
    const user = (typeof Auth !== "undefined" && Auth.getUser()) || null;
    const name = user?.full_name?.split(" ")[0] || "there";

    addMessage("bot",
      `Hey ${name}! 👋 I'm **CraftBot**, your AI guide on CraftCycle Market.\n\nI can help you find scrap materials, suggest DIY product ideas, explain the platform, and more. What can I help you with today?`
    );

    // Show quick prompts
    quickEl.innerHTML = QUICK_PROMPTS.map(p =>
      `<button class="cb-quick-btn" onclick="window._cbQuick('${p}')">${p}</button>`
    ).join("");
  }

  // ── Add message to UI ─────────────────────────────────────
  function addMessage(role, text) {
    // Remove quick prompts after first user message
    if (role === "user") quickEl.innerHTML = "";

    const isBot = role === "bot";
    const el = document.createElement("div");
    el.className = `cb-msg ${role}`;

    // Format markdown-lite: **bold**, newlines
    const formatted = text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");

    el.innerHTML = `
      <div class="cb-msg-avatar notranslate">${isBot ? "🤖" : "👤"}</div>
      <div class="cb-bubble">${formatted}</div>
    `;
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return el;
  }

  // ── Typing indicator ──────────────────────────────────────
  function showTyping() {
    const el = document.createElement("div");
    el.className = "cb-msg bot";
    el.id = "cb-typing";
    el.innerHTML = `
      <div class="cb-msg-avatar notranslate">🤖</div>
      <div class="cb-typing"><span></span><span></span><span></span></div>
    `;
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function hideTyping() {
    const el = document.getElementById("cb-typing");
    if (el) el.remove();
  }

  // ── Send message ──────────────────────────────────────────
  async function sendMessage(text) {
    text = text.trim();
    if (!text || isTyping) return;

    // No API key needed for local mock mode
    // if (!OPENAI_KEY) {
    //   noKeyEl.style.display = "block";
    //   addMessage("bot", "⚠️ I can't respond yet — the OpenAI API key isn't configured. Please add it to `js/config.js` and refresh.");
    //   return;
    // }

    addMessage("user", text);
    inputEl.value = "";
    inputEl.style.height = "auto";

    // Add to conversation history
    conversation.push({ role: "user", content: text });

    isTyping = true;
    sendBtn.disabled = true;
    statusText.textContent = "Thinking…";
    showTyping();

    try {
      // Call backend API instead of mock logic
      const response = await fetch(`${CONFIG.API_BASE_URL}/chatbot/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: conversation.slice(0, -1) // Send history without current message
        })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        const reply = data.reply;
        conversation.push({ role: "assistant", content: reply });
        hideTyping();
        addMessage("bot", reply);
      } else {
        throw new Error(data.message || 'API Error');
      }

      // Badge if panel is closed
      if (!isOpen) {
        unreadBadge.style.display = "flex";
        unreadBadge.textContent = "1";
      }

    } catch (err) {
      console.error("Chatbot Error:", err);
      hideTyping();
      
      // Provide more specific error feedback based on what happened
      let errorMsg = "I'm having trouble connecting to my AI core. Please check your internet or try again later! ⚙️";
      if (err.message && err.message !== "API Error") {
        errorMsg = `⚠️ AI Engine Error: ${err.message}`;
      } else if (err.status === 429) {
        errorMsg = "⚠️ Too many messages! Please wait a moment before asking more questions.";
      }
      
      addMessage("bot", errorMsg);
    } finally {
      isTyping = false;
      sendBtn.disabled = false;
      statusText.textContent = "Online — Ask me anything!";
    }
  }

  // ── Global handlers (needed for inline onclick) ───────────
  window._cbSend = () => sendMessage(inputEl.value);
  window._cbQuick = (text) => sendMessage(text);
  window._cbKeydown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputEl.value);
    }
  };

  // Auto-resize textarea
  inputEl.addEventListener("input", () => {
    inputEl.style.height = "auto";
    inputEl.style.height = Math.min(inputEl.scrollHeight, 100) + "px";
  });

  // ── Show unread dot after 5s if not opened ────────────────
  setTimeout(() => {
    if (!isOpen) {
      unreadBadge.style.display = "flex";
      unreadBadge.textContent = "1";
    }
  }, 5000);

})();
