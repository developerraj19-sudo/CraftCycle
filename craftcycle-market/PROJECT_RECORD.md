# 🌿 CraftCycle: Project Record & Core Features

This document serves as a centralized record of the **CraftCycle Market** platform, detailing its core features, architectural logic, and sample code implementations.

---

## 🏗️ Project Overview
**CraftCycle** is a premium circular economy platform where users transform waste into wealth. It connects scrap sellers with upcyclers and provides AI-powered tools to facilitate sustainable craft businesses.

### Tech Stack
- **Backend**: Python (Flask), SQLAlchemy, JWT, OpenAI API.
- **Frontend**: Vanilla JS, Modern CSS (Glassmorphism), HTML5.
- **Database**: Supabase (PostgreSQL) + Supabase Storage.
- **Deployment**: Render (Backend), Netlify (Frontend).

---

## 📁 Project Structure (Full Codebase)

```text
CraftCycle/
├── backend/                # Flask API (Python)
│   ├── app.py              # Main Entry & Blueprint registration
│   ├── config.py           # Multi-env config (Dev/Prod/Test)
│   ├── extensions.py       # DB, JWT, Mail & Limiter init
│   ├── models/             # SQLAlchemy Models (User, Product, Order, etc.)
│   ├── routes/             # API Endpoints (Auth, Marketplace, Scanner, etc.)
│   ├── utils/              # Validators, Storage & Error helpers
│   ├── requirements.txt    # Python Dependencies
│   └── Procfile            # Deployment config for Render/Heroku
├── frontend/               # Single Page Application (SPA) feel
│   ├── home.html           # Landing Page (SEO optimized)
│   ├── assets/             # Shared Assets
│   │   ├── css/style.css   # Main Design System (Glassmorphism)
│   │   ├── js/api.js       # Reusable API fetcher logic
│   │   ├── js/config.js    # Frontend environment constants
│   │   └── js/utils.js     # Shared UI components & Sidebar logic
│   ├── pages/              # Feature Pages
│   │   ├── marketplace.html# Scrap & Product grid
│   │   ├── scanner.html    # AI Vision interface
│   │   ├── tutorial-hub.html# DIY Education center
│   │   └── challenges.html # Gamification UI
│   └── netlify.toml        # Frontend deployment config
├── database/               # SQL Scripts
│   └── schema.sql          # Base PostgreSQL schema
├── supabase/               # Backend-as-a-Service config
│   └── migrations/         # Versioned DB migrations
└── .env                    # System Secrets (Template in config section)
```

---

## 📋 Advanced Feature Snippets

These snippets cover the complex business logic found in the marketplace and order management systems.

### **1. Marketplace Filtering (Backend)**
Efficiently filtering listings by category, quality, price range, and location.
```python
@marketplace_bp.get("/")
def list_listings():
    category = request.args.get("category")
    city     = request.args.get("city")
    q = ScrapMaterial.query.filter_by(status="active")
    
    if category: q = q.filter(ScrapMaterial.category == category)
    if city:     q = q.filter(ScrapMaterial.location_city.ilike(f"%{city}%"))
    
    paged = q.paginate(page=1, per_page=20)
    return jsonify(listings=[l.to_dict() for l in paged.items]), 200
```

### **2. Order Status Management**
Handling transitions between 'Pending', 'Paid', and 'Completed' states.
```python
@orders_bp.put("/<int:id>/status")
@jwt_required()
def update_status(id):
    order = Order.query.get_or_404(id)
    new_status = request.get_json().get("status")
    
    if new_status in ["shipped", "completed"]:
        order.status = new_status
        db.session.commit()
        return jsonify(message=f"Order is now {new_status}"), 200
```

### **3. Seller Listing Integration**
Sending complex form data (including images and tags) from the frontend.
```javascript
const postListing = async (formData) => {
  const res = await apiRequest('POST', '/marketplace/', { 
    body: {
      title: formData.get('title'),
      category: formData.get('category'),
      price_per_kg: parseFloat(formData.get('price')),
      images: [formData.get('image_url')] // Supabase URL
    }
  });
  if (res.message) Toast.success("Listed!", "Material is live.");
};
```

---

## 🔐 Authentication Logic (Full Stack)

CraftCycle uses a unified authentication flow across the backend and frontend, ensuring secure access to marketplace and AI features.

### **1. Backend API (Flask)**
Handles password hashing, validation, and JWT generation.

#### **Registration (POST /auth/register)**
```python
@auth_bp.post("/register")
def register():
    data = request.get_json()
    user = User(email=data['email'], username=data['username'], role=data.get('role', 'buyer'))
    user.set_password(data['password']) # Hashes using Bcrypt
    user.green_coins = 100 # Welcome Bonus
    db.session.add(user)
    db.session.commit()
    
    access = create_access_token(identity=str(user.id))
    return jsonify(message="Success", access_token=access), 201
```

#### **Login (POST /auth/login)**
```python
@auth_bp.post("/login")
def login():
    data = request.get_json()
    user = User.query.filter((User.email == data['email']) | (User.username == data['email'])).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify(error="Invalid credentials"), 401
        
    access = create_access_token(identity=str(user.id))
    return jsonify(message="Welcome back!", access_token=access, user=user.to_dict()), 200
```

### **2. Frontend Integration (JS)**
Manages local storage and automatic token injection via the `AuthAPI` module.

#### **Auth Client Logic**
```javascript
const AuthAPI = {
  async register(data) {
    const res = await apiRequest('POST', '/auth/register', { body: data });
    if (res.access_token) Auth.setTokens(res.access_token, res.refresh_token);
    return res;
  },
  
  async login(email, password) {
    const res = await apiRequest('POST', '/auth/login', { body: { email, password } });
    if (res.access_token) {
      Auth.setTokens(res.access_token, res.refresh_token);
      Auth.setUser(res.user);
    }
    return res;
  }
};
```

---

## 🛠️ Developer Cheat Sheet (Quick Snippets)

Use these snippets to quickly implement common UI patterns and business logic across the platform.

### **1. Feedback & Notifications**
```javascript
// Success message (green)
Toast.success("Success!", "Project saved to your board.");

// Error message (red)
Toast.error("Failed", "Please check your internet connection.");

// Info message (cyan)
Toast.info("AI Scanner", "Analyzing your material...");
```

### **2. Data Formatting**
```javascript
// Currency (₹1,200)
const price = formatINR(1200);

// Weight (1.5 kg or 2.3 tonnes)
const weight = formatKg(1500);

// Time (2h ago, 3d ago)
const time = timeAgo("2023-10-27T10:00:00Z");
```

### **3. Access Control (Guards)**
```javascript
// Redirect to login if guest
requireAuth();

// Redirect to dashboard if not admin
requireAdmin();

// Simple check
if (isLoggedIn()) { /* show private content */ }
```

### **4. UI Interactions**
```javascript
// Trigger the AI Chatbot programmatically
window.dispatchEvent(new CustomEvent('chatbot:toggle'));

// Manual Coin Award (Frontend update + backend call)
CoinManager.award(50, 'bonus_achievement');
```

---

## 🔑 Authentication & Security

CraftCycle uses **JWT (JSON Web Tokens)** for stateless authentication and **Bcrypt** for password hashing.

### **1. Secure User Registration**
Includes validation, uniqueness checks, and the automated "Welcome Coins" reward system.
```python
@auth_bp.post("/register")
def register():
    # ... validation logic ...
    user = User(email=email, username=username, role=role)
    user.set_password(password) # Bcrypt Hashing
    user.green_coins = 100 # Welcome Bonus
    
    db.session.add(user)
    db.session.commit()
    
    access = create_access_token(identity=str(user.id))
    return jsonify(user=user.to_dict(), access_token=access), 201
```

### **2. Real-time Notifications (Supabase)**
Listens for database changes (like coin updates) and reflects them in the UI instantly.
```javascript
function initCoinRealtime() {
  const supabase = createClient(URL, KEY);
  supabase
    .channel('public:coin_transactions')
    .on('postgres_changes', { event: 'INSERT', filter: `user_id=eq.${user.id}` }, (payload) => {
        // Update UI Balance and show Toast
        window.dispatchEvent(new CustomEvent('coins:updated', { detail: { coins: payload.new.balance } }));
        Toast.success("Green Coins +", `You earned ${payload.new.amount} coins!`);
    })
    .subscribe();
}
```

---

## ⚙️ Environment Configuration (.env)

The project requires the following environment variables to be fully functional:

```bash
# Core
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@db-host:5432/postgres

# Security
SECRET_KEY=your_flask_secret
JWT_SECRET_KEY=your_jwt_secret

# External APIs
OPENAI_API_KEY=sk-proj-... # For AI Scanner & Chatbot
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_ANON_KEY=...

# Rewards Logic
WELCOME_COINS=100
SCAN_COINS=2
```

---

## 🧩 The "Heart" of the Code (Core Samples)

If you are looking for the absolute "main thing" in the codebase, these are the core patterns used across the entire platform.

### **1. The Universal API Fetcher (Frontend)**
Found in `api.js`, this pattern handles all communication, including automatic JWT token injection and error handling.
```javascript
async function apiRequest(method, path, { body, formData } = {}) {
  const headers = {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': body ? 'application/json' : undefined
  };
  
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : (formData || null)
  });

  if (response.status === 401) { /* Auto-logout or Refresh logic */ }
  return await response.json();
}
```

### **2. Standard Protected API Route (Backend)**
Found in every route (Auth, Marketplace, etc.), this is the backbone of the server logic.
```python
@blueprint.post("/action")
@jwt_required()
def handle_action():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Core Logic
    result = perform_business_logic(user_id, data)
    db.session.commit()
    
    return jsonify(result), 200
```

### **3. Secure Model Pattern (Database)**
The pattern for handling sensitive data and business logic within SQLAlchemy models.
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(255))
    green_coins = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def award_coins(self, amount, category, desc):
        self.green_coins += amount
        # Log transaction...
```

---

## 🎨 Main Pages & UI Logic

The platform uses a consistent **Glassmorphism** design and a dynamic layout system. Below are the primary code blocks for the main pages.

### **1. Circular Marketplace (Grid & Rendering)**
Handles the dynamic rendering of scrap materials and DIY products with skeleton loaders for premium feel.
```javascript
async function loadListings() {
  const data = await MarketplaceAPI.list(filters);
  const items = data.listings.map(l => `
    <div class="listing-card card">
      <div class="listing-thumb"><img src="${l.image}"></div>
      <div class="listing-body">
        <div class="listing-title">${l.title}</div>
        <div class="listing-price-main">₹${l.price_per_kg}</div>
        <div class="listing-seller">👤 ${l.seller.name}</div>
      </div>
    </div>
  `).join('');
  document.getElementById("listings-grid").innerHTML = items;
}
```

### **2. AI Trash Scanner (Vision UI)**
Manages the image upload state, real-time "scanning" animation, and result display.
```javascript
async function analyze() {
  const fd = new FormData();
  fd.append("image", selectedFile);
  
  showScanOverlay(); // Trigger scanning animation
  const data = await ScannerAPI.analyze(fd);
  
  // Render results with material detection & 3 upcycling ideas
  renderResults(data.material_detected, data.suggestions);
  awardScanCoins(); // Award Green Coins for participating
}
```

### **3. Dynamic Sidebar & Layout System**
A single source of truth for the app shell, managing guest vs. logged-in states and role-based access.
```javascript
function renderSidebarNav() {
  const logged = Auth.isLoggedIn();
  const user = Auth.getUser();
  
  let html = `
    <a href="home.html" class="nav-item">🏠 Home</a>
    <a href="marketplace.html" class="nav-item">🏪 Marketplace</a>
  `;
  
  if (logged) {
    html += `<a href="dashboard.html" class="nav-item">📊 Dashboard</a>`;
    if (user.role === 'seller') {
      html += `<a href="my-products.html" class="nav-item">📦 My Store</a>`;
    }
  }
  document.querySelector('.sidebar-nav').innerHTML = html;
}
```

---

## 🗄️ Database & Security

CraftCycle uses **Supabase (PostgreSQL)** with SQLAlchemy for structured data and **Supabase Storage** for assets.

### **1. Database Connection & Config**
Managed in `config.py`, with automatic protocol correction for SQLAlchemy.
```python
# Database URL handling
_db_url = os.getenv("DATABASE_URL", "")
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URI = _db_url
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_recycle": 280,
    "pool_pre_ping": True,
}
```

### **2. Extension Initialization**
Located in `extensions.py`, ensuring a clean separation of concerns.
```python
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

db      = SQLAlchemy()
jwt     = JWTManager()
bcrypt  = Bcrypt()
```

---

## 🏛️ Core UI Architecture (HTML)

All pages follow a consistent **App Shell** pattern with a blurred glass navbar and a responsive sidebar.

### **1. Base Page Structure**
A representative structure found in `home.html` and `marketplace.html`.
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <link rel="stylesheet" href="assets/css/style.css" />
  <script src="assets/js/api.js"></script>
</head>
<body>
  <div class="app-shell">
    <!-- Shared Sidebar -->
    <aside class="sidebar">
      <nav class="sidebar-nav"></nav>
    </aside>

    <!-- Main Content Area -->
    <div class="main-content">
      <header class="topbar">
        <div class="user-avatar" data-user-avatar></div>
      </header>
      <main>
        <!-- Page Content -->
      </main>
    </div>
  </div>
</body>
</html>
```

### **2. UI State Attributes**
The system uses `data-*` attributes for reactive UI updates without a heavy framework.
- `[data-user-name]`: Automatically filled with user's full name.
- `[data-user-coins]`: Real-time ticking counter for Green Coins.
- `[data-user-avatar]`: Dynamic avatar (initials or image).

---

## 🚀 Main Features & Sample Code

### 1. AI Trash Scanner 🔍
Users upload photos of waste materials, and the AI (GPT-4o) identifies the material and suggests 3 upcycling product ideas.

#### **Backend Logic (Flask)**
```python
@scanner_bp.post("/analyze")
@jwt_required()
def analyze():
    # ... image validation ...
    client = OpenAI(api_key=current_app.config["OPENAI_API_KEY"])
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                {"type": "text", "text": "Analyse waste and provide 3 upcycling ideas in JSON format."}
            ]
        }]
    )
    # Save to history and award Green Coins
    return jsonify(result)
```

#### **Sample Output (JSON)**
```json
{
  "material_detected": "Clear Plastic PET Bottles",
  "suggestions": [
    {
      "title": "Self-Watering Planter",
      "difficulty": "easy",
      "estimated_resale_value_inr": 150,
      "waste_kg_saved": 0.2
    }
  ],
  "coins_earned": 2
}
```

---

### 2. CraftBot AI Assistant 🤖
A floating chatbot that provides DIY guidance, platform support, and eco-tips.

#### **Backend Implementation**
Uses a multi-model fallback strategy (`gpt-4o` -> `gpt-4o-mini` -> `gpt-3.5-turbo`) to ensure high availability.

#### **Frontend Widget (Vanilla JS)**
```javascript
// self-injecting widget
(function() {
    const BOT_NAME = "CraftBot 🌿";
    // Inject CSS & HTML
    // Handle message sending to /api/chat
    async function sendMessage(text) {
        const response = await fetch('/api/v1/chatbot/chat', {
            method: 'POST',
            body: JSON.stringify({ message: text })
        });
        const data = await response.json();
        addMessage("bot", data.reply);
    }
})();
```

---

### 3. Circular Marketplace 🏪
A dual-sided market for **Scrap Materials** (bottles, cardboard, metal) and **Upcycled Products** (finished crafts).

#### **Key Database Model (SQLAlchemy)**
```python
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20)) # 'scrap' or 'upcycled'
    price = db.Column(db.Float, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
```

---

### 4. Backend Reliability & Sync ⚙️
Automatic database schema migrations and health monitoring.

#### **Self-Healing Database Sync**
The app automatically detects and adds missing columns during startup, ensuring production stability on platforms like Render.
```python
with app.app_context():
    db.create_all()
    # Manual ALTER TABLE commands for mission-critical columns
    db.session.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivery_fee NUMERIC(10,2)"))
    db.session.commit()
```

---

## 🛠️ Developer Cheat Sheet (Integration Snippets)

### **1. Protected API Call (Frontend)**
```javascript
async function fetchProtected(url, options = {}) {
    const token = localStorage.getItem('token');
    return fetch(url, {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });
}
```

### **2. Awarding Green Coins (Backend)**
```python
user.award_coins(amount=10, type="challenge", description="Completed Daily Task")
db.session.commit()
```

### **3. Environment Config (.env)**
```bash
FLASK_APP=app.py
DATABASE_URL=postgresql://user:pass@db.supabase.co:5432/postgres
OPENAI_API_KEY=sk-proj-...
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_KEY=ey...
```

---

## 📈 Project Metrics Tracked
- **Waste Diverted**: Total kg of waste upcycled.
- **Green Wealth**: Total revenue generated by sellers.
- **AI Accuracy**: Success rate of material identification.

---
*Created by Antigravity AI for CraftCycle Project Records.*
