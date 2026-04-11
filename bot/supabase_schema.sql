-- =====================================================
-- Supabase Database Schema for SMM Telegram Bot
-- =====================================================
-- Execute this SQL in your Supabase SQL Editor
-- =====================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT DEFAULT 'لا يوجد',
    first_name TEXT DEFAULT 'مستخدم',
    balance DECIMAL(15, 6) DEFAULT 0.0,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Services table (API ID + display name for the bot UI)
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    service_api_id INTEGER NOT NULL,
    service_name TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(category_id, service_api_id)
);

-- Existing projects: add display name column if the table was created from an older schema
ALTER TABLE services ADD COLUMN IF NOT EXISTS service_name TEXT NOT NULL DEFAULT '';

-- Pricing rules table (per-service pricing)
CREATE TABLE IF NOT EXISTS pricing_rules (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    pricing_type TEXT CHECK (pricing_type IN ('fixed', 'percentage')) NOT NULL,
    price_value DECIMAL(15, 6), -- For fixed pricing
    percentage_value DECIMAL(5, 2), -- For percentage pricing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(service_id)
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    service_api_id INTEGER NOT NULL,
    original_price DECIMAL(15, 6) NOT NULL,
    final_price DECIMAL(15, 6) NOT NULL,
    quantity INTEGER NOT NULL,
    link TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    order_api_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Settings table (key-value store)
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Channels table
CREATE TABLE IF NOT EXISTS channels (
    id SERIAL PRIMARY KEY,
    channel_username TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_services_category_id ON services(category_id);
CREATE INDEX IF NOT EXISTS idx_pricing_rules_service_id ON pricing_rules(service_id);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_users_balance ON users(balance);

-- =====================================================
-- Insert default settings
-- =====================================================
INSERT INTO settings (key, value) 
VALUES ('new_user_notifications', 'true')
ON CONFLICT (key) DO NOTHING;

-- =====================================================
-- Schema verification query
-- =====================================================
-- Run this to verify all tables were created:
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- ORDER BY table_name;
