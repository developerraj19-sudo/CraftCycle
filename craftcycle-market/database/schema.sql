-- ============================================================
--  CRAFTCYCLE MARKET — PostgreSQL Schema for Supabase
--  Run in Supabase SQL Editor in this exact order
-- ============================================================

-- 1. USERS
CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    username        VARCHAR(50)  UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(100),
    role            TEXT DEFAULT 'buyer' CHECK (role IN ('buyer','seller','admin')),
    avatar_url      VARCHAR(255),
    bio             TEXT,
    phone           VARCHAR(20),
    city            VARCHAR(100),
    state           VARCHAR(100),
    green_coins     INTEGER DEFAULT 0 CHECK (green_coins >= 0),
    is_active       BOOLEAN DEFAULT TRUE,
    is_verified     BOOLEAN DEFAULT FALSE,
    reset_token     VARCHAR(255),
    reset_expires   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 2. SELLER_PROFILES
CREATE TABLE seller_profiles (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             BIGINT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    shop_name           VARCHAR(150),
    shop_description    TEXT,
    specialty           VARCHAR(100),
    total_sales         INTEGER DEFAULT 0,
    total_waste_saved   DECIMAL(10,2) DEFAULT 0,
    rating              DECIMAL(3,2) DEFAULT 0,
    rating_count        INTEGER DEFAULT 0,
    is_approved         BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- 3. SCRAP_MATERIALS (Marketplace)
CREATE TABLE scrap_materials (
    id              BIGSERIAL PRIMARY KEY,
    seller_id       BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    category        TEXT CHECK (category IN (
                        'wood','metal','plastic','fabric','paper',
                        'glass','e-waste','organic','rubber','other')),
    quality         TEXT CHECK (quality IN ('excellent','good','fair','poor')),
    quantity_kg     DECIMAL(10,2),
    price_per_kg    DECIMAL(10,2),
    total_price     DECIMAL(10,2),
    location_city   VARCHAR(100),
    location_state  VARCHAR(100),
    is_barter_ok    BOOLEAN DEFAULT FALSE,
    barter_for      VARCHAR(300),
    images          JSONB DEFAULT '[]',
    tags            JSONB DEFAULT '[]',
    status          TEXT DEFAULT 'active' CHECK (status IN ('active','sold','suspended')),
    view_count      INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 4. PRODUCTS (DIY upcycled goods)
CREATE TABLE products (
    id              BIGSERIAL PRIMARY KEY,
    seller_id       BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    category        VARCHAR(100),
    price           DECIMAL(10,2) NOT NULL,
    stock_qty       INTEGER DEFAULT 1,
    images          JSONB DEFAULT '[]',
    materials_used  TEXT,
    waste_kg_saved  DECIMAL(10,2) DEFAULT 0,
    co2_kg_saved    DECIMAL(10,2) DEFAULT 0,
    time_to_make_h  DECIMAL(5,1),
    difficulty      TEXT CHECK (difficulty IN ('easy','medium','hard')),
    status          TEXT DEFAULT 'active' CHECK (status IN ('active','sold','suspended','pending')),
    view_count      INTEGER DEFAULT 0,
    wish_count      INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 5. ORDERS
CREATE TABLE orders (
    id               BIGSERIAL PRIMARY KEY,
    buyer_id         BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_amount     DECIMAL(10,2) NOT NULL,
    platform_fee     DECIMAL(10,2) DEFAULT 0,
    status           TEXT DEFAULT 'pending' CHECK (
                         status IN ('pending','paid','shipped','delivered','cancelled','refunded')),
    payment_id       VARCHAR(255),
    payment_method   VARCHAR(50),
    shipping_address JSONB,
    notes            TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- 6. ORDER_ITEMS
CREATE TABLE order_items (
    id          BIGSERIAL PRIMARY KEY,
    order_id    BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id  BIGINT NOT NULL REFERENCES products(id),
    seller_id   BIGINT NOT NULL REFERENCES users(id),
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    unit_price  DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL
);

-- 7. REVIEWS
CREATE TABLE reviews (
    id          BIGSERIAL PRIMARY KEY,
    reviewer_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id  BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    order_id    BIGINT REFERENCES orders(id),
    rating      SMALLINT CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 8. SCANNER_HISTORY
CREATE TABLE scanner_history (
    id                BIGSERIAL PRIMARY KEY,
    user_id           BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    image_hash        VARCHAR(255),
    image_url         VARCHAR(500),
    material_detected VARCHAR(255),
    suggestions       JSONB DEFAULT '[]',
    coins_earned      INTEGER DEFAULT 0,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

-- 9. COIN_TRANSACTIONS
CREATE TABLE coin_transactions (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount      INTEGER NOT NULL,
    balance     INTEGER NOT NULL,
    type        TEXT CHECK (type IN (
                    'welcome','scan','sale','purchase',
                    'challenge','review','referral','admin','refund')),
    description VARCHAR(255),
    ref_id      BIGINT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 10. CHALLENGES
CREATE TABLE challenges (
    id          BIGSERIAL PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    description TEXT,
    theme       VARCHAR(100),
    prize_coins INTEGER DEFAULT 100,
    prize_desc  VARCHAR(300),
    max_entries INTEGER,
    entry_count INTEGER DEFAULT 0,
    status      TEXT DEFAULT 'upcoming' CHECK (
                    status IN ('upcoming','active','voting','ended')),
    starts_at   TIMESTAMPTZ,
    ends_at     TIMESTAMPTZ,
    created_by  BIGINT REFERENCES users(id),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 11. WISHLISTS
CREATE TABLE wishlists (
    user_id    BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    added_at   TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, product_id)
);

-- 12. PLATFORM_SETTINGS
CREATE TABLE platform_settings (
    setting_key VARCHAR(100) PRIMARY KEY,
    value       TEXT NOT NULL,
    description TEXT
);

-- ============================================================
--  SEED DATA
-- ============================================================

INSERT INTO platform_settings (setting_key, value, description) VALUES
('commission_rate',        '10',  'Platform fee percentage'),
('welcome_coins',          '100', 'Coins on registration'),
('scan_coins',             '2',   'Coins per AI scan'),
('sale_coins_rate',        '5',   'Coins per 100 INR of sale'),
('scanner_rate_limit',     '5',   'Max scans per hour per user'),
('max_images_per_listing', '5',   'Max images per listing');

-- Admin user (password: Admin@2024)
INSERT INTO users (username, email, password_hash, full_name, role, is_active, is_verified, green_coins) VALUES
('admin', 'admin@craftcycle.com', 
 '$2b$12$LQv3c1yqBWVHxkd0LQ.VoO26S2Vr9VpCR4JDXxyvQH.qVn9YA0F9K', 
 'CraftCycle Admin', 'admin', TRUE, TRUE, 9999);

-- Demo seller
INSERT INTO users (username, email, password_hash, full_name, role, city, state, is_active, is_verified, green_coins) VALUES
('riya_creates', 'riya@craftcycle.com', 
 '$2b$12$LQv3c1yqBWVHxkd0LQ.VoO26S2Vr9VpCR4JDXxyvQH.qVn9YA0F9K', 
 'Riya Sharma', 'seller', 'Bangalore', 'Karnataka', TRUE, TRUE, 250);

INSERT INTO seller_profiles (user_id, shop_name, shop_description, specialty, is_approved)
VALUES (2, 'Riya Creates', 'Upcycled home decor and art from waste materials', 'Wood, Fabric, Paper', TRUE);

-- Demo listings
INSERT INTO scrap_materials (seller_id, title, description, category, quality, quantity_kg, price_per_kg, total_price, location_city, location_state, status) VALUES
(2, 'Reclaimed Teak Wood Planks', 'Old teak wood from demolished furniture.', 'wood', 'good', 25.0, 45.0, 1125.0, 'Bangalore', 'Karnataka', 'active');

INSERT INTO products (seller_id, title, description, category, price, materials_used, waste_kg_saved, co2_kg_saved, difficulty, status) VALUES
(2, 'Reclaimed Wood Wall Clock', 'Unique handmade clock.', 'Home Decor', 1299.0, 'Reclaimed Wood', 1.5, 1.2, 'easy', 'active');


-- ============================================================
--  SUPABASE REALTIME & SECURITY (RLS)
-- ============================================================

-- Enable Realtime for coin_transactions
-- This allows the frontend to listen for live balance updates
ALTER TABLE coin_transactions REPLICA IDENTITY FULL;
BEGIN;
  -- Drop if exists to avoid errors on re-run
  DROP PUBLICATION IF EXISTS supabase_realtime;
  CREATE PUBLICATION supabase_realtime FOR TABLE coin_transactions;
COMMIT;

-- Enable RLS on coin_transactions
ALTER TABLE coin_transactions ENABLE ROW LEVEL SECURITY;

-- Allow users to read ONLY their own transactions
CREATE POLICY "Users can view own transactions" 
ON coin_transactions FOR SELECT 
USING (true); -- For v1.0 demonstration, allowing read access. 
-- In production with Supabase Auth, replace with: USING (auth.uid()::text = user_id::text);
