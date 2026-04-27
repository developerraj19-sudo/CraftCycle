/**
 * frontend/assets/js/config.js
 * ───────────────────────────
 * Central configuration for the frontend.
 */

const CONFIG = {
  // Use http://localhost:5000/api/v1 for local development
  // Use https://craftcycle.onrender.com/api/v1 for production
  API_BASE_URL: "https://craftcycle.onrender.com/api/v1",

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
