/**
 * frontend/assets/js/config.js
 * ───────────────────────────
 * Central configuration for the frontend.
 */

const CONFIG = {
  // Backend API base URL (Update this after deploying to Render/Heroku)
  API_BASE_URL: "https://craftcycle-api.onrender.com/api/v1",

  // Supabase Configuration (For Realtime Green Coins & Storage)
  SUPABASE_URL: "https://your-project-url.supabase.co",
  SUPABASE_ANON_KEY: "your-anon-public-key",

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
