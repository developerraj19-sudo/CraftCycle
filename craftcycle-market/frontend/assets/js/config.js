/**
 * frontend/assets/js/config.js
 * ───────────────────────────
 * Central configuration for the frontend.
 */

const CONFIG = {
  // Automatically detect the right API base URL:
  // - localhost → local dev server
  // - craftcycle.onrender.com → same-origin (relative path works)
  // - craftcycle.pages.dev or any other host → must call Render explicitly
  API_BASE_URL: (() => {
    const h = window.location.hostname;
    if (h === 'localhost' || h === '127.0.0.1') return 'http://localhost:5000/api/v1';
    if (h.includes('onrender.com')) return '/api/v1';       // same-origin on Render
    return 'https://craftcycle.onrender.com/api/v1';        // pages.dev → Render
  })(),

  // Supabase Configuration (For Realtime Green Coins & Storage)
  SUPABASE_URL: "https://spyqshsiyojmqphfbcac.supabase.co",
  SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNweXFzaHNpeW9qbXFwaGZiY2FjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY2NjIyMTgsImV4cCI6MjA5MjIzODIxOH0.TuYKoJRfEGy5M3_p6DWgjP9P272F7jD-5PfsMZGQFZg",

  // localStorage keys
  KEYS: {
    ACCESS_TOKEN: "cc_access_token",
    REFRESH_TOKEN: "cc_refresh_token",
    USER: "cc_user",
  },

  // Platform info
  PLATFORM_FEE_PERCENT: 10,
  CURRENCY: "₹",
  CURRENCY_LOCALE: "en-IN",
};
