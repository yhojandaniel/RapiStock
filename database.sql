-- 1. Extensiones necesarias (Para UUIDs rápidos)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Configuración de función para actualizar modified_at automáticamente
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ==========================================
-- TABLA: PRODUCTS
-- ==========================================
CREATE TABLE products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(50) NOT NULL UNIQUE, -- Indexado automáticamente por ser UNIQUE
    name VARCHAR(150) NOT NULL,
    stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0), -- Constraint: No stock negativo
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0), -- 10 dígitos, 2 decimales
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- Indice para búsquedas rápidas por nombre (ej: autocompletado en el POS)
CREATE INDEX idx_products_name ON products(name);

-- ==========================================
-- TABLA: SELLERS
-- ==========================================
CREATE TABLE sellers (
    seller_id SERIAL PRIMARY KEY,
    dni VARCHAR(15) NOT NULL UNIQUE,
    fullname VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW() -- Agregué timestamps que faltaban
);

-- ==========================================
-- TABLA: ORDERS
-- ==========================================
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    seller_id INT NOT NULL REFERENCES sellers(seller_id) ON DELETE RESTRICT,
    status VARCHAR(20) NOT NULL CHECK (status IN ('paid', 'refunded')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- Optimización: Indexar la FK
CREATE INDEX idx_orders_seller_id ON orders(seller_id);
-- Optimización: Indexar por fecha (para reportes de ventas del día)
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- ==========================================
-- TABLA: ORDER_DETAILS
-- ==========================================
CREATE TABLE order_details (
    order_detail_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    current_price DECIMAL(10, 2) NOT NULL, -- Snapshot del precio
    product_quantity INT NOT NULL CHECK (product_quantity > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- Optimización: Indexar las FKs
CREATE INDEX idx_order_details_order_id ON order_details(order_id);
CREATE INDEX idx_order_details_product_id ON order_details(product_id);

-- ==========================================
-- TABLA: REFUNDS
-- ==========================================
CREATE TABLE refunds (
    refund_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id) ON DELETE RESTRICT,
    amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_refunds_order_id ON refunds(order_id);

-- ==========================================
-- TABLA: REFUND_DETAILS
-- ==========================================
CREATE TABLE refund_details (
    refund_detail_id SERIAL PRIMARY KEY,
    refund_id INT NOT NULL REFERENCES refunds(refund_id) ON DELETE CASCADE,
    order_detail_id INT NOT NULL REFERENCES order_details(order_detail_id) ON DELETE RESTRICT,
    refunded_price DECIMAL(10, 2) NOT NULL,
    product_quantity INT NOT NULL CHECK (product_quantity > 0),
    status VARCHAR(20) NOT NULL CHECK (status IN ('same', 'opened')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_refund_details_refund_id ON refund_details(refund_id);
CREATE INDEX idx_refund_details_order_detail_id ON refund_details(order_detail_id);

-- ==========================================
-- TRIGGERS (Automatización de modified_at)
-- ==========================================
-- Esto hace que modified_at se actualice solo cuando haces un UPDATE
CREATE TRIGGER update_products_modtime BEFORE UPDATE ON products FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
CREATE TRIGGER update_sellers_modtime BEFORE UPDATE ON sellers FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
CREATE TRIGGER update_orders_modtime BEFORE UPDATE ON orders FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
CREATE TRIGGER update_order_details_modtime BEFORE UPDATE ON order_details FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
CREATE TRIGGER update_refunds_modtime BEFORE UPDATE ON refunds FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
CREATE TRIGGER update_refund_details_modtime BEFORE UPDATE ON refund_details FOR EACH ROW EXECUTE PROCEDURE update_modified_column();