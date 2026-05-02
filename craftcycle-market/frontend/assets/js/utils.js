/**
 * frontend/js/utils.js
 * ─────────────────────
 * Shared utility functions loaded on every page.
 * Depends on: config.js, api.js
 */


// ═══════════════════════════════════════════════════════════════
//  TOAST NOTIFICATIONS
// ═══════════════════════════════════════════════════════════════
const Toast = (() => {
  let container;

  function getContainer() {
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      Object.assign(container.style, {
        position: "fixed", top: "20px", right: "20px",
        zIndex: "9999", display: "flex", flexDirection: "column", gap: "10px",
        maxWidth: "360px",
      });
      document.body.appendChild(container);
    }
    return container;
  }

  const COLORS = {
    success: { bg: "#00FF88", text: "#050D1A" },
    error: { bg: "#FF4D4D", text: "#fff" },
    info: { bg: "#00D4FF", text: "#050D1A" },
    warning: { bg: "#F59E0B", text: "#050D1A" },
  };

  const ICONS = { success: "✅", error: "❌", info: "ℹ️", warning: "⚠️" };

  function show(type, title, message = "", duration = 4000) {
    const c = COLORS[type] || COLORS.info;
    const toast = document.createElement("div");

    Object.assign(toast.style, {
      background: "#111B2E",
      border: `1px solid ${c.bg}40`,
      borderLeft: `3px solid ${c.bg}`,
      borderRadius: "8px",
      padding: "14px 16px",
      display: "flex",
      alignItems: "flex-start",
      gap: "10px",
      boxShadow: `0 4px 20px rgba(0,0,0,0.4)`,
      opacity: "0",
      transform: "translateX(40px)",
      transition: "all 0.25s ease",
      cursor: "pointer",
    });

    toast.innerHTML = `
      <span style="font-size:1.1rem;flex-shrink:0">${ICONS[type]}</span>
      <div style="flex:1">
        <div style="font-weight:700;font-size:0.875rem;color:#E8F4FF;margin-bottom:2px">${title}</div>
        ${message ? `<div style="font-size:0.8rem;color:#7A9AB8">${message}</div>` : ""}
      </div>
      <span style="color:#7A9AB8;font-size:0.9rem;flex-shrink:0;cursor:pointer" onclick="this.parentElement.remove()">×</span>
    `;

    toast.onclick = () => {
      toast.style.opacity = "0"; toast.style.transform = "translateX(40px)";
      setTimeout(() => toast.remove(), 250);
    };

    getContainer().appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
      toast.style.opacity = "1";
      toast.style.transform = "translateX(0)";
    });

    // Auto-dismiss
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(40px)";
      setTimeout(() => toast.remove(), 250);
    }, duration);
  }

  return {
    success: (title, msg, d) => show("success", title, msg, d),
    error: (title, msg, d) => show("error", title, msg, d),
    info: (title, msg, d) => show("info", title, msg, d),
    warning: (title, msg, d) => show("warning", title, msg, d),
  };
})();


// ═══════════════════════════════════════════════════════════════
//  AUTH GUARDS
// ═══════════════════════════════════════════════════════════════
function requireAuth() {
  if (!Auth.isLoggedIn()) {
    const returnTo = encodeURIComponent(window.location.pathname + window.location.search);
    window.location.href = `auth.html?return=${returnTo}`;
  }
}

function requireAdmin() {
  const user = Auth.getUser();
  if (!user || user.role !== "admin") {
    Toast.error("Access Denied", "Admin privileges required.");
    setTimeout(() => { window.location.href = "dashboard.html"; }, 1500);
  }
}

function redirectIfLoggedIn(dest = "dashboard.html") {
  if (Auth.isLoggedIn()) window.location.href = dest;
}


// ═══════════════════════════════════════════════════════════════
//  FORMAT HELPERS
// ═══════════════════════════════════════════════════════════════
function formatINR(amount) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency", currency: "INR", maximumFractionDigits: 0,
  }).format(amount);
}

function formatKg(kg) {
  if (kg >= 1000) return `${(kg / 1000).toFixed(1)} tonnes`;
  return `${parseFloat(kg).toFixed(1)} kg`;
}

function timeAgo(isoString) {
  if (!isoString) return "–";
  const seconds = Math.floor((Date.now() - new Date(isoString)) / 1000);
  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  return new Date(isoString).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "2-digit" });
}

function truncate(str, n = 80) {
  if (!str) return "";
  return str.length > n ? str.slice(0, n - 1) + "…" : str;
}


// ═══════════════════════════════════════════════════════════════
//  DOM HELPERS
// ═══════════════════════════════════════════════════════════════
function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

/** Animate a number counting up from 0 to `target`. */
function animateCount(el, target, prefix = "", suffix = "", decimals = 0) {
  const duration = 1200;
  const start = Date.now();
  function tick() {
    const elapsed = Date.now() - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);   // ease-out cubic
    const current = target * eased;
    el.textContent = prefix + current.toFixed(decimals) + suffix;
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

/** Fill [data-user-*] elements from stored user object. */
function populateUserInfo() {
  const user = Auth.getUser();
  if (!user) return;

  document.querySelectorAll("[data-user-name]").forEach(el => {
    el.textContent = user.full_name || user.username || "User";
  });
  document.querySelectorAll("[data-user-role]").forEach(el => {
    el.textContent = user.role.charAt(0).toUpperCase() + user.role.slice(1);
  });
  document.querySelectorAll("[data-user-coins]").forEach(el => {
    el.textContent = (user.green_coins || 0).toLocaleString();
  });
  document.querySelectorAll("[data-user-avatar]").forEach(el => {
    if (user.avatar_url) {
      el.innerHTML = `<img src="${user.avatar_url}" alt="avatar" style="width:100%;height:100%;border-radius:50%;object-fit:cover">`;
    } else {
      el.textContent = (user.full_name || user.username || "U")[0].toUpperCase();
    }
  });

  // Role-based UI constraints
  if (user.role === 'buyer') {
    // Hide 'List Material' button in marketplace
    const listBtn = document.getElementById("list-btn");
    if (listBtn) listBtn.style.display = "none";

    // Hide seller-specific stats & sections on Dashboard
    const productsGrid = document.getElementById("products-grid");
    if (productsGrid && productsGrid.parentElement) {
      productsGrid.parentElement.style.display = "none";
    }
    const statRevenue = document.getElementById("stat-revenue");
    if (statRevenue && statRevenue.closest(".stat-card")) statRevenue.closest(".stat-card").style.display = "none";
    const statListings = document.getElementById("stat-listings");
    if (statListings && statListings.closest(".stat-card")) statListings.closest(".stat-card").style.display = "none";
    const revenueChart = document.getElementById("revenue-chart");
    if (revenueChart && revenueChart.closest(".card.chart-container")) revenueChart.closest(".card.chart-container").style.display = "none";
  }
}

/** 
 * renderSidebarNav()
 * Single source of truth for all sidebar navigation links.
 * Handles: guest vs logged-in, role-based sections, active page, and footer.
 */
function renderSidebarNav() {
  const nav = document.querySelector('.sidebar-nav');
  if (!nav) return;

  const logged = typeof Auth !== 'undefined' && Auth.isLoggedIn();
  const user = logged ? Auth.getUser() : null;

  // Work out prefix: home.html is one level up from pages/
  const path = window.location.pathname;
  const isHome = path.endsWith('/') || path.endsWith('index.html') || path.endsWith('home.html');
  const p = isHome ? 'pages/' : '';

  // ── Build nav HTML ──────────────────────────────────────────
  const homeLink = isHome ? 'home.html' : '../home.html';

  let html = `<div class="nav-section-label">Explore</div>
    <a href="${homeLink}"           class="nav-item"><span class="nav-icon">🏠</span><span class="nav-label"> Home</span></a>
    <a href="${p}marketplace.html"  class="nav-item"><span class="nav-icon">🏪</span><span class="nav-label"> Marketplace</span></a>
    <a href="${p}scanner.html"      class="nav-item"><span class="nav-icon">🔍</span><span class="nav-label"> AI Scanner</span></a>
    <a href="${p}nearby.html"       class="nav-item"><span class="nav-icon">🗺️</span><span class="nav-label"> Nearby Dealers</span></a>
    <a href="${p}tutorial-hub.html" class="nav-item"><span class="nav-icon">🎓</span><span class="nav-label"> Tutorial Hub</span></a>
    <a href="${p}community.html"    class="nav-item"><span class="nav-icon">🌐</span><span class="nav-label"> Community</span></a>`;

  if (logged) {
    // Challenges (available to all logged-in)
    html += `
      <div class="nav-section-label" style="margin-top:var(--s4)">Community Activity</div>
      <a href="${p}challenges.html" class="nav-item"><span class="nav-icon">🏆</span><span class="nav-label"> Challenges</span></a>`;

    // Store section (sellers only)
    if (user?.role === 'seller') {
      html += `
        <div class="nav-section-label" style="margin-top:var(--s4)">My Store</div>
        <a href="${p}my-products.html" class="nav-item"><span class="nav-icon">📦</span><span class="nav-label"> My Products</span></a>
        <a href="${p}orders.html"      class="nav-item"><span class="nav-icon">🛒</span><span class="nav-label"> Orders</span></a>`;
    }

    // Account section
    html += `
      <div class="nav-section-label" style="margin-top:var(--s4)">Account</div>
      <a href="${p}dashboard.html" class="nav-item"><span class="nav-icon">📊</span><span class="nav-label"> Dashboard</span></a>
      <a href="${p}buyer-orders.html" class="nav-item"><span class="nav-icon">🛍️</span><span class="nav-label"> My Orders</span></a>
      <a href="${p}profile.html"   class="nav-item"><span class="nav-icon">👤</span><span class="nav-label"> Profile</span></a>
      <a href="${p}coins.html"     class="nav-item"><span class="nav-icon">🪙</span><span class="nav-label"> Green Coins</span></a>`;

    if (user?.role === 'admin') {
      html += `<a href="${p}admin.html" class="nav-item" style="color:var(--yellow)"><span class="nav-icon">⚙️</span><span class="nav-label"> System Admin</span></a>`;
    }
  } else {
    // Guest: show login/signup prompt at bottom of nav
    html += `
      <div class="nav-section-label" style="margin-top:var(--s4)">Account</div>
      <a href="${p}auth.html?tab=login"    class="nav-item"><span class="nav-icon">🔑</span><span class="nav-label"> Login</span></a>
      <a href="${p}auth.html?tab=register" class="nav-item"><span class="nav-icon">✨</span><span class="nav-label"> Sign Up Free</span></a>`;
  }

  nav.innerHTML = html;

  // ── Inject desktop collapse toggle into sidebar logo area ──
  const sidebar = document.querySelector('.sidebar');
  if (sidebar && !sidebar.querySelector('.sidebar-collapse-btn')) {
    const logoEl = sidebar.querySelector('.sidebar-logo');

    // Wrap the existing logo-mark in a sidebar-logo-row div (if not already)
    if (logoEl && !logoEl.querySelector('.sidebar-logo-row')) {
      const logoMark = logoEl.querySelector('.logo-mark');
      const row = document.createElement('div');
      row.className = 'sidebar-logo-row';

      // Create the collapse button
      const btn = document.createElement('button');
      btn.className = 'sidebar-collapse-btn';
      btn.title = 'Collapse sidebar';
      btn.setAttribute('aria-label', 'Toggle sidebar');
      btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 19l-7-7 7-7"/><path d="M19 19l-7-7 7-7"/></svg>`;

      // Move logo-mark into the row, then append btn
      if (logoMark) {
        row.appendChild(logoMark);
      }
      row.appendChild(btn);
      logoEl.insertBefore(row, logoEl.firstChild);

      btn.addEventListener('click', () => {
        const collapsed = sidebar.classList.toggle('collapsed');
        localStorage.setItem('cc_sidebar_collapsed', collapsed ? '1' : '0');
        btn.setAttribute('title', collapsed ? 'Expand sidebar' : 'Collapse sidebar');
      });
    }

    // Restore persisted collapsed state
    if (localStorage.getItem('cc_sidebar_collapsed') === '1') {
      sidebar.classList.add('collapsed');
    }
  }


  // ── Render footer ──────────────────────────────────────────
  renderSidebarFooter(logged, user, p);

  // ── Mark active link ───────────────────────────────────────
  setActiveNav();
}

/** Render the sidebar footer based on auth state */
function renderSidebarFooter(logged, user, p) {
  const footer = document.querySelector('.sidebar-footer');
  if (!footer) return;

  if (logged && user) {
    const initials = (user.full_name || user.username || 'U')[0].toUpperCase();
    footer.innerHTML = `
      <div class="sidebar-user">
        <div class="user-avatar" data-user-avatar>${initials}</div>
        <div class="sidebar-user-info">
          <div style="font-size:0.875rem;font-weight:600;line-height:1.3" data-user-name>${user.full_name || user.username || 'User'}</div>
          <div style="font-size:0.72rem;color:var(--text-3)">🪙 <span data-user-coins>${(user.green_coins || 0).toLocaleString()}</span></div>
        </div>
      </div>
      <button class="btn btn-ghost btn-sm w-full" style="margin-top:var(--s3)" data-logout>🚪 Logout</button>`;

    // Re-wire the logout button since we just recreated it
    footer.querySelector('[data-logout]')?.addEventListener('click', async () => {
      try { await AuthAPI.logout(); } catch (_) { }
      Auth.clear();
      window.location.href = `${p}auth.html`;
    });
  } else {
    footer.innerHTML = '';
  }
}

/** Highlight the nav link that matches the current page. */
function setActiveNav() {
  const current = window.location.pathname.split('/').pop() || 'home.html';
  document.querySelectorAll('.nav-item').forEach(a => {
    const href = (a.getAttribute('href') || '').split('/').pop();
    a.classList.toggle('active', href === current);
  });
}


/** Mobile sidebar toggle — with Android swipe, ESC, and scroll-lock. */
function initMobileSidebar() {
  const hamburger = document.querySelector(".hamburger");
  const sidebar = document.querySelector(".sidebar");
  const overlay = document.querySelector(".sidebar-overlay");
  if (!hamburger || !sidebar) return;

  function openSidebar() {
    sidebar.classList.add("open");
    overlay?.classList.add("active");
    document.body.style.overflow = "hidden";
    hamburger.setAttribute("aria-expanded", "true");
    hamburger.setAttribute("aria-label", "Close navigation");
  }

  function closeSidebar() {
    sidebar.classList.remove("open");
    overlay?.classList.remove("active");
    document.body.style.overflow = "";
    hamburger.setAttribute("aria-expanded", "false");
    hamburger.setAttribute("aria-label", "Open navigation");
  }

  function toggleSidebar() {
    if (sidebar.classList.contains("open")) closeSidebar();
    else openSidebar();
  }

  // Hamburger button click
  hamburger.setAttribute("aria-controls", "main-sidebar");
  hamburger.setAttribute("aria-expanded", "false");
  hamburger.setAttribute("aria-label", "Open navigation");
  sidebar.id = sidebar.id || "main-sidebar";

  hamburger.addEventListener("click", toggleSidebar);

  // Overlay click closes sidebar
  overlay?.addEventListener("click", closeSidebar);

  // ESC key closes sidebar
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && sidebar.classList.contains("open")) closeSidebar();
  });

  // ── Android / Touch: swipe-left to close sidebar ──────────────
  let touchStartX = 0;
  let touchStartY = 0;

  sidebar.addEventListener("touchstart", (e) => {
    touchStartX = e.changedTouches[0].screenX;
    touchStartY = e.changedTouches[0].screenY;
  }, { passive: true });

  sidebar.addEventListener("touchend", (e) => {
    const dx = e.changedTouches[0].screenX - touchStartX;
    const dy = Math.abs(e.changedTouches[0].screenY - touchStartY);
    // Swipe left ≥ 60px and mostly horizontal → close
    if (dx < -60 && dy < 80) closeSidebar();
  }, { passive: true });

  // ── Edge swipe-right from left edge to open sidebar ───────────
  document.addEventListener("touchstart", (e) => {
    if (e.changedTouches[0].screenX < 20) {
      touchStartX = e.changedTouches[0].screenX;
      touchStartY = e.changedTouches[0].screenY;
    }
  }, { passive: true });

  document.addEventListener("touchend", (e) => {
    const dx = e.changedTouches[0].screenX - touchStartX;
    const dy = Math.abs(e.changedTouches[0].screenY - touchStartY);
    if (touchStartX < 20 && dx > 60 && dy < 80) openSidebar();
  }, { passive: true });

  // Auto-close sidebar nav links (for single-page feel on mobile)
  sidebar.querySelectorAll(".nav-item").forEach(link => {
    link.addEventListener("click", () => {
      if (window.innerWidth < 768) closeSidebar();
    });
  });
}

/** Scroll-reveal via IntersectionObserver. */
function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add("visible");
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll(".reveal").forEach(el => observer.observe(el));
}


// ═══════════════════════════════════════════════════════════════
//  GLOBAL LOGOUT LISTENER
// ═══════════════════════════════════════════════════════════════
window.addEventListener("auth:logout", () => {
  Auth.clear();
  Toast.warning("Session expired", "Please log in again.");
  setTimeout(() => { window.location.href = "auth.html"; }, 1500);
});


// ═══════════════════════════════════════════════════════════════
//  GLOBAL COIN UPDATE LISTENER
//  Any page that loads utils.js will react to coin changes
//  fired by CoinManager.award() on the scanner or other pages.
// ═══════════════════════════════════════════════════════════════


// ═══════════════════════════════════════════════════════════════
//  SUPABASE REALTIME
// ═══════════════════════════════════════════════════════════════
let supabaseClient = null;

/** 
 * Initialize Supabase Realtime to listen for Green Coin updates.
 */
function initCoinRealtime() {
  if (!CONFIG.SUPABASE_URL || CONFIG.SUPABASE_URL.includes("your-project")) return;
  if (!supabase || typeof supabase.createClient !== 'function') return;

  const user = Auth.getUser();
  if (!user || !user.id) return;

  if (!supabaseClient) {
    supabaseClient = supabase.createClient(CONFIG.SUPABASE_URL, CONFIG.SUPABASE_ANON_KEY);
  }

  // Subscribe to changes in coin_transactions for this user
  supabaseClient
    .channel('public:coin_transactions')
    .on('postgres_changes', {
      event: 'INSERT',
      schema: 'public',
      table: 'coin_transactions',
      filter: `user_id=eq.${user.id}`
    }, (payload) => {
      const newTx = payload.new;
      console.log("Realtime Coin Update received:", newTx);

      // Fire the global event to trigger UI updates across the page
      window.dispatchEvent(new CustomEvent('coins:updated', {
        detail: { coins: newTx.balance }
      }));

      // Update local storage so the state persists across page reloads
      const updatedUser = { ...user, green_coins: newTx.balance };
      localStorage.setItem(CONFIG.KEYS.USER, JSON.stringify(updatedUser));

      Toast.success("Green Coins +", `You earned ${newTx.amount} coins from ${newTx.type}!`);
    })
    .subscribe();
}


// ═══════════════════════════════════════════════════════════════
//  INIT ON EVERY PAGE
// ═══════════════════════════════════════════════════════════════
document.addEventListener("DOMContentLoaded", () => {
  populateUserInfo();
  renderSidebarNav();
  setActiveNav();
  initMobileSidebar();
  initScrollReveal();

  // ── Logout ──────────────────────────────────────────────────
  document.querySelectorAll("[data-logout]").forEach(btn => {
    btn.addEventListener("click", async () => {
      try { await AuthAPI.logout(); } catch (_) { }
      Auth.clear();
      window.location.href = "auth.html";
    });
  });

  // ── Global Notifications Dropdown ─────────────────────────────
  function createNotifDropdown() {
    let dropdown = document.getElementById('global-notif-dropdown');
    if (!dropdown) {
      dropdown = document.createElement('div');
      dropdown.id = 'global-notif-dropdown';
      dropdown.className = 'notif-dropdown';
      dropdown.innerHTML = `
        <div class="notif-header">
          <span>Notifications</span>
          <button class="btn btn-ghost btn-sm" id="mark-read-btn" style="font-size:0.7rem;padding:2px 8px;height:auto">Mark all read</button>
        </div>
        <div class="notif-list">
          <div class="notif-item" style="cursor:pointer;" onclick="window.location.href='tutorial-hub.html'">
            <div class="notif-icon">🌱</div>
            <div class="notif-content">
              <strong>Welcome to CraftCycle!</strong>
              <p>Explore the DIY Hub and Marketplace to get started.</p>
              <div class="notif-time">Just now</div>
            </div>
          </div>
          <div class="notif-item" style="cursor:pointer;" onclick="window.location.href='scanner.html'">
            <div class="notif-icon" style="background:var(--cyan-glow);color:var(--cyan);border-color:rgba(0,212,255,0.2)">🪙</div>
            <div class="notif-content">
              <strong style="color:var(--cyan)">Earn Green Coins</strong>
              <p>Scan your first recyclable item using the AI Scanner to earn your first coins.</p>
              <div class="notif-time" style="color:var(--text-3)">5m ago</div>
            </div>
          </div>
        </div>
      `;
      document.body.appendChild(dropdown);

      // Handle clicking "Mark all read"
      document.getElementById('mark-read-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.querySelector('.notif-list').innerHTML = `
          <div style="padding:var(--s6);text-align:center;color:var(--text-3);font-size:0.8rem">
            No new notifications
          </div>`;
        document.querySelectorAll('.notif-dot').forEach(el => el.style.display = 'none');
      });
    }
    return dropdown;
  }

  // Wire up global notif buttons
  document.querySelectorAll(".notif-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation(); // prevent document body click from immediately closing it
      const dropdown = createNotifDropdown();
      const isShowing = dropdown.classList.contains('show');

      // Toggle dropdown
      if (!isShowing) {
        dropdown.classList.add('show');
      } else {
        dropdown.classList.remove('show');
      }
    });
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    const dropdown = document.getElementById('global-notif-dropdown');
    if (dropdown && dropdown.classList.contains('show')) {
      if (!dropdown.contains(e.target)) {
        dropdown.classList.remove('show');
      }
    }
  });

  // ── Realtime coins ──────────────────────────────────────────
  if (isLoggedIn()) {
    initCoinRealtime();
  }
});


// ═══════════════════════════════════════════════════════════════
//  UI EVENT LISTENERS
// ═══════════════════════════════════════════════════════════════
window.addEventListener('coins:updated', (e) => {
  const { coins } = e.detail;

  // Update every [data-user-coins] element on the page (sidebar, topbar, profile)
  document.querySelectorAll('[data-user-coins]').forEach(el => {
    // Animate the number ticking up
    const from = parseInt(el.textContent.replace(/,/g, '')) || 0;
    const to = coins;
    if (from === to) { el.textContent = to.toLocaleString(); return; }
    const duration = 800;
    const start = Date.now();
    function tick() {
      const progress = Math.min((Date.now() - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(from + (to - from) * eased).toLocaleString();
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);

    // Flash the element green briefly
    el.style.transition = 'color .2s';
    el.style.color = 'var(--green)';
    setTimeout(() => { el.style.color = ''; }, 1500);
  });
});


// ═══════════════════════════════════════════════════════════════
//  PUBLIC PAGE AUTH HELPERS
// ═══════════════════════════════════════════════════════════════

/**
 * requireAuthForAction(message)
 * Call this before any action that needs auth on a public page.
 * Returns true if authenticated, false (and redirects) if not.
 */
function requireAuthForAction(message = "Please sign in to continue.") {
  if (typeof Auth !== "undefined" && Auth.isLoggedIn()) return true;
  // Save the current URL so we can return after login
  const returnUrl = encodeURIComponent(window.location.href);
  Toast.info("Login Required", message);
  setTimeout(() => {
    window.location.href = `auth.html?return=${returnUrl}`;
  }, 1200);
  return false;
}

/**
 * isLoggedIn() - simple check
 */
function isLoggedIn() {
  return typeof Auth !== "undefined" && Auth.isLoggedIn();
}

/**
 * updatePublicNav()
 * On public pages, shows login/signup CTA if not logged in,
 * or normal user info if logged in.
 */
function updatePublicNav() {
  const logged = isLoggedIn();
  const user = logged ? Auth.getUser() : null;

  // Sidebar footer
  const footer = document.querySelector(".sidebar-footer");
  if (footer) {
    if (logged) {
      // Normal logged-in state
      const av = footer.querySelector("[data-user-avatar]");
      const nm = footer.querySelector("[data-user-name]");
      if (av && user?.full_name) av.textContent = user.full_name[0];
      if (nm && user?.full_name) nm.textContent = user.full_name;
    } else {
      // Public: hide the footer buttons completely (nav items are already used for this)
      footer.innerHTML = '';
    }
  }

  // Topbar right — replace avatar with login CTA if not logged in
  if (!logged) {
    document.querySelectorAll(".topbar-right [data-user-avatar]").forEach(el => el.remove());
    const topbarRight = document.querySelector(".topbar-right");
    if (topbarRight && !topbarRight.querySelector(".pub-login-cta")) {
      const cta = document.createElement("div");
      cta.className = "pub-login-cta";
      cta.style.cssText = "display:flex;gap:var(--s2);align-items:center";
      cta.innerHTML = `
        <a href="auth.html?tab=login"    class="btn btn-ghost  btn-sm">Login</a>
        <a href="auth.html?tab=register" class="btn btn-primary btn-sm">Sign Up</a>
      `;
      topbarRight.appendChild(cta);
    }
  }
}
