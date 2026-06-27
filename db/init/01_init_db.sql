-- Database Initialization Schema
-- Target Database Engine: PostgreSQL
-- Redesigned Clean Database Schema Specification

-- Table: customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50),
    country VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: products
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: orders
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    order_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    total_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (total_amount >= 0)
);

-- Table: order_items
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0)
);

-- Indices for Join Keys and Filtering Performance
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_total_amount ON orders(total_amount);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_customers_country ON customers(country);

-- Analytical View 1: Customer Order Summary
CREATE OR REPLACE VIEW customer_order_summary AS
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email,
    c.city,
    c.state,
    c.country,
    COUNT(o.order_id)::INTEGER AS total_orders,
    COALESCE(SUM(o.total_amount), 0.00) AS total_revenue,
    CASE 
        WHEN COUNT(o.order_id) > 0 THEN ROUND(COALESCE(SUM(o.total_amount), 0.00) / COUNT(o.order_id), 2)
        ELSE 0.00
    END AS average_order_value,
    MIN(o.order_date) AS first_order_date,
    MAX(o.order_date) AS last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id;

-- Analytical View 2: Product Sales Summary
CREATE OR REPLACE VIEW product_sales_summary AS
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    p.price,
    COALESCE(SUM(oi.quantity), 0)::INTEGER AS units_sold,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0.00) AS total_revenue,
    COUNT(DISTINCT oi.order_id)::INTEGER AS total_orders
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id;

-- Role Definition and Permission Allocation
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'dataset_manager') THEN
        CREATE ROLE dataset_manager WITH LOGIN PASSWORD 'dataset_manager_pass';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'db_readonly') THEN
        CREATE ROLE db_readonly WITH LOGIN PASSWORD 'readonly_user_pass';
    END IF;
END
$$;

-- Grant dataset_manager schema usage and creation rights
GRANT CONNECT ON DATABASE ai_sql_agent TO dataset_manager;
GRANT USAGE, CREATE ON SCHEMA public TO dataset_manager;
GRANT ALL PRIVILEGES ON SCHEMA public TO dataset_manager;


-- Grant Connection & Usage Permissions
GRANT CONNECT ON DATABASE ai_sql_agent TO db_readonly;
GRANT USAGE ON SCHEMA public TO db_readonly;

-- Revoke all modifications to ensure least-privilege integrity
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM db_readonly;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM db_readonly;

-- Allocate Read-Only Access
GRANT SELECT ON ALL TABLES IN SCHEMA public TO db_readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO db_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO db_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO db_readonly;
