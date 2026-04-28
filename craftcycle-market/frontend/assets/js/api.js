/**
 * frontend/js/api.js
 * ────────────────────
 * API client with:
 *   - Automatic JWT token injection
 *   - Silent token refresh on 401
 *   - Typed methods for every backend endpoint
 *
 * Depends on: config.js
 */

// ═══════════════════════════════════════════════════════════════
//  TOKEN STORAGE
// ═══════════════════════════════════════════════════════════════
const Auth = {
  getAccessToken()  { return localStorage.getItem(CONFIG.KEYS.ACCESS_TOKEN);  },
  getRefreshToken() { return localStorage.getItem(CONFIG.KEYS.REFRESH_TOKEN); },
  getUser()         {
    try { return JSON.parse(localStorage.getItem(CONFIG.KEYS.USER) || "null"); }
    catch { return null; }
  },

  setTokens(access, refresh) {
    localStorage.setItem(CONFIG.KEYS.ACCESS_TOKEN,  access);
    localStorage.setItem(CONFIG.KEYS.REFRESH_TOKEN, refresh);
  },

  setUser(user) {
    localStorage.setItem(CONFIG.KEYS.USER, JSON.stringify(user));
  },

  clear() {
    localStorage.removeItem(CONFIG.KEYS.ACCESS_TOKEN);
    localStorage.removeItem(CONFIG.KEYS.REFRESH_TOKEN);
    localStorage.removeItem(CONFIG.KEYS.USER);
  },

  isLoggedIn() { return !!this.getAccessToken(); },
};


// ═══════════════════════════════════════════════════════════════
//  CORE FETCH WRAPPER
// ═══════════════════════════════════════════════════════════════
let _refreshing = false;          // prevents multiple simultaneous refreshes
let _refreshQueue = [];           // queued requests waiting for new token

async function apiRequest(method, path, { body, formData, params } = {}) {
  const url = new URL(`${CONFIG.API_BASE_URL}${path}`, window.location.origin);

  // Append query params
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, v);
    });
  }

  // Build headers
  const headers = {};
  const token = Auth.getAccessToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (body)  headers["Content-Type"]  = "application/json";

  // Build fetch options
  const options = { method, headers };
  if (body)     options.body = JSON.stringify(body);
  if (formData) options.body = formData;   // no Content-Type header for multipart

  let response = await fetch(url.toString(), options);

  // ── Auto-refresh on 401 ────────────────────────────────────
  if (response.status === 401 && Auth.getRefreshToken()) {
    if (_refreshing) {
      // Wait for the in-progress refresh, then retry
      await new Promise((resolve, reject) => _refreshQueue.push({ resolve, reject }));
      return apiRequest(method, path, { body, formData, params });
    }

    _refreshing = true;
    try {
      const refreshRes = await fetch(`${CONFIG.API_BASE_URL}/auth/refresh`, {
        method: "POST",
        headers: { Authorization: `Bearer ${Auth.getRefreshToken()}` },
      });

      if (refreshRes.ok) {
        const { access_token } = await refreshRes.json();
        Auth.setTokens(access_token, Auth.getRefreshToken());
        _refreshQueue.forEach(p => p.resolve());
        _refreshQueue = [];
        _refreshing   = false;

        // Retry original request with new token
        headers["Authorization"] = `Bearer ${access_token}`;
        options.headers = headers;
        response = await fetch(url.toString(), options);
      } else {
        // Refresh also failed — log out
        _refreshQueue.forEach(p => p.reject());
        _refreshQueue = [];
        _refreshing   = false;
        Auth.clear();
        window.dispatchEvent(new CustomEvent("auth:logout"));
        throw { status: 401, message: "Session expired. Please log in again." };
      }
    } catch (err) {
      _refreshing = false;
      throw err;
    }
  }

  // ── Parse response ─────────────────────────────────────────
  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : { message: await response.text() };

  if (!response.ok) {
    let msg = data.error || data.message || "Request failed";
    if (data.details) {
      const details = Object.entries(data.details).map(([k, v]) => `${k}: ${v}`).join(", ");
      msg += ` (${details})`;
    }
    const err = new Error(msg);
    err.status = response.status;
    err.data   = data;
    throw err;
  }

  return data;
}

// Convenience methods
const api = {
  get:    (path, params)       => apiRequest("GET",    path, { params }),
  post:   (path, body)         => apiRequest("POST",   path, { body }),
  put:    (path, body)         => apiRequest("PUT",    path, { body }),
  delete: (path)               => apiRequest("DELETE", path),
  upload: (path, formData)     => apiRequest("POST",   path, { formData }),
};


// ═══════════════════════════════════════════════════════════════
//  TYPED API MODULES
// ═══════════════════════════════════════════════════════════════

/** Authentication */
const AuthAPI = {
  async login(email, password) {
    const data = await api.post("/auth/login", { email, password });
    Auth.setTokens(data.access_token, data.refresh_token);
    Auth.setUser(data.user);
    return data;
  },

  async register(payload) {
    const data = await api.post("/auth/register", payload);
    Auth.setTokens(data.access_token, data.refresh_token);
    Auth.setUser(data.user);
    return data;
  },

  me:             () => api.get("/auth/me"),
  logout:         () => { Auth.clear(); return api.post("/auth/logout", {}); },
  forgotPassword: (email) => api.post("/auth/forgot", { email }),
  resetPassword:  (token, password) => api.post("/auth/reset", { token, password }),
};


/** Scrap Marketplace */
const MarketplaceAPI = {
  list:   (params) => api.get("/marketplace/", params),
  get:    (id)     => api.get(`/marketplace/${id}`),
  create: (data)   => api.post("/marketplace/", data),
  update: (id, data) => api.put(`/marketplace/${id}`, data),
  delete: (id)     => api.delete(`/marketplace/${id}`),
  categories: ()   => api.get("/marketplace/categories"),
};


/** Products */
const ProductsAPI = {
  list:   (params) => api.get("/products/", params),
  get:    (id)     => api.get(`/products/${id}`),
  create: (data)   => api.post("/products/", data),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id)     => api.delete(`/products/${id}`),
};


/** AI Scanner */
const ScannerAPI = {
  analyze: (formData) => api.upload("/scanner/analyze", formData),
  history: ()         => api.get("/scanner/history"),
};


/** Admin */
const AdminAPI = {
  dashboard:       ()            => api.get("/admin/dashboard"),
  analytics:       ()            => api.get("/admin/analytics"),
  users:           (params)      => api.get("/admin/users", params),
  updateUser:      (id, data)    => api.put(`/admin/users/${id}`, data),
  products:        (params)      => api.get("/admin/products", params),
  moderateProduct: (id, status)  => api.put(`/admin/products/${id}`, { status }),
};


/** Orders */
const OrdersAPI = {
  create:       (payload) => api.post("/orders/", payload),
  list:         ()        => api.get("/orders/"),
  sellerOrders: ()        => api.get("/orders/seller"),
};
