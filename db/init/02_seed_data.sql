-- Database seed script for AI SQL Query Agent
-- Generates enhanced products, customers, orders, and order items.
-- Production-Ready Balanced Data Seeding

-- 1. Insert 52 Products with Categories and Brand details
INSERT INTO products (product_name, category, brand, price) VALUES
-- Electronics (12 products)
('QuantumBook Pro 15', 'Electronics', 'Apple', 1499.99),
('SuperPixel 8 Pro Smartphone', 'Electronics', 'Google', 899.99),
('AeroSound Max Noise Cancelling Headphones', 'Electronics', 'Sony', 349.99),
('SonicCharge 65W GaN Charger', 'Electronics', 'Anker', 39.99),
('AeroWatch Active Smartwatch', 'Electronics', 'Garmin', 199.99),
('OptiView 27-inch 4K Monitor', 'Electronics', 'Dell', 449.99),
('NeoKey Mechanic Keyboard RGB', 'Electronics', 'Logitech', 129.99),
('SwiftGlide Wireless Mouse', 'Electronics', 'Logitech', 59.99),
('MegaDrive 2TB External SSD', 'Electronics', 'Samsung', 179.99),
('StreamCam Ultra HD Webcam', 'Electronics', 'Logitech', 99.99),
('VibeBar 2.1 Soundbar Speaker', 'Electronics', 'Sonos', 149.99),
('SecureVault Smart Home Lock', 'Electronics', 'August', 249.99),
-- Apparel (10 products)
('Apex Dry-Fit Running Shirt', 'Apparel', 'Nike', 34.99),
('ComfyStride Cushioned Socks (3-Pack)', 'Apparel', 'Nike', 14.99),
('MetroSlim Stretch Chino Pants', 'Apparel', 'Everlane', 59.99),
('ThermalGuard Fleece Jacket', 'Apparel', 'Patagonia', 89.99),
('AllWeather Waterproof Windbreaker', 'Apparel', 'Columbia', 119.99),
('FlexFit Yoga Pants Activewear', 'Apparel', 'Lululemon', 49.99),
('UrbanClassic Leather Belt', 'Apparel', 'Fossil', 29.99),
('HydroShield Breathable Hiking Shoes', 'Apparel', 'Merrell', 139.99),
('WarmCozy Wool Beanie Hat', 'Apparel', 'Carhartt', 19.99),
('SleekFit Polarized Sunglasses', 'Apparel', 'Oakley', 79.99),
-- Home & Kitchen (10 products)
('ChefMaster 10-Piece Cookware Set', 'Home & Kitchen', 'All-Clad', 299.99),
('BrewPulse 12-Cup Drip Coffee Maker', 'Home & Kitchen', 'Keurig', 79.99),
('PreserveFresh Vacuum Sealer Machine', 'Home & Kitchen', 'FoodSaver', 119.99),
('PureAir HEPA Air Purifier', 'Home & Kitchen', 'Dyson', 189.99),
('AutoClean Robot Vacuum & Mop', 'Home & Kitchen', 'iRobot', 399.99),
('ThermoCore Digital Food Scale', 'Home & Kitchen', 'Ozeri', 24.99),
('BlendForce 1200W Blender', 'Home & Kitchen', 'Vitamix', 89.99),
('SlicePrecise 6-Piece Knife Set', 'Home & Kitchen', 'Wüsthof', 149.99),
('EcoClean Microfiber Cleaning Cloths (12-Pack)', 'Home & Kitchen', 'Simplehuman', 15.99),
('SleepCloud Memory Foam Pillow', 'Home & Kitchen', 'Tempur-Pedic', 49.99),
-- Books (10 products)
('The Art of Clean Code', 'Books', 'O''Reilly Media', 24.99),
('Data Science from Scratch', 'Books', 'Manning Publications', 39.99),
('Architecting Cloud Solutions', 'Books', 'No Starch Press', 44.99),
('Introduction to Machine Learning', 'Books', 'O''Reilly Media', 49.99),
('SQL Performance Explained', 'Books', 'No Starch Press', 29.99),
('Building Microservices with Go', 'Books', 'Manning Publications', 34.99),
('Designing Data-Intensive Applications', 'Books', 'O''Reilly Media', 49.99),
('Mastering Python Design Patterns', 'Books', 'Manning Publications', 39.99),
('The Product Manager Handbook', 'Books', 'O''Reilly Media', 19.99),
('Effective DevOps Practices', 'Books', 'Manning Publications', 34.99),
-- Sports & Outdoors (10 products)
('PeakAdventure 2-Person Camping Tent', 'Sports & Outdoors', 'Coleman', 129.99),
('TrekComfort Adjustable Hiking Backpack', 'Sports & Outdoors', 'Osprey', 89.99),
('HydroHydrate 32oz Insulated Bottle', 'Sports & Outdoors', 'Hydro Flask', 29.99),
('TrailGrip Carbon Fiber Trekking Poles', 'Sports & Outdoors', 'Black Diamond', 69.99),
('EverReady LED Headlamp 300 Lumens', 'Sports & Outdoors', 'Petzl', 24.99),
('FitStretch Premium Yoga Mat', 'Sports & Outdoors', 'Lululemon', 39.99),
('CoreBurn Resistant Band Set', 'Sports & Outdoors', 'Bowflex', 19.99),
('SpeedJump Speed Rope', 'Sports & Outdoors', 'Rogue Fitness', 14.99),
('GripStrong Anti-Slip Gym Gloves', 'Sports & Outdoors', 'Under Armour', 17.99),
('ProFlex Adjustable Dumbbells (Pair)', 'Sports & Outdoors', 'Bowflex', 299.99);

-- 2. Generate exactly 100 Customers with geographic distribution
DO $$
DECLARE
    first_names text[] := ARRAY['Liam', 'Olivia', 'Noah', 'Emma', 'Oliver', 'Ava', 'Elijah', 'Charlotte', 'William', 'Sophia', 'James', 'Amelia', 'Benjamin', 'Isabella', 'Lucas', 'Mia', 'Henry', 'Evelyn', 'Alexander', 'Harper'];
    last_names text[] := ARRAY['Smith', 'Jones', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White'];
    
    countries text[] := ARRAY['United States', 'Canada', 'United Kingdom', 'Germany', 'Australia'];
    
    us_cities text[] := ARRAY['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'];
    us_states text[] := ARRAY['NY', 'CA', 'IL', 'TX', 'AZ'];
    
    ca_cities text[] := ARRAY['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa'];
    ca_states text[] := ARRAY['ON', 'BC', 'QC', 'AB', 'ON'];
    
    uk_cities text[] := ARRAY['London', 'Manchester', 'Birmingham', 'Leeds', 'Glasgow'];
    uk_states text[] := ARRAY['ENG', 'ENG', 'ENG', 'ENG', 'SCT'];
    
    de_cities text[] := ARRAY['Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne'];
    de_states text[] := ARRAY['BE', 'BY', 'HH', 'HE', 'NW'];
    
    au_cities text[] := ARRAY['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide'];
    au_states text[] := ARRAY['NSW', 'VIC', 'QLD', 'WA', 'SA'];

    f_name text;
    l_name text;
    c_city text;
    s_state text;
    c_country text;
    geo_idx integer;
    country_idx integer;
    created_ts timestamp with time zone;
BEGIN
    FOR i IN 1..100 LOOP
        f_name := first_names[1 + floor(random() * 20)::integer];
        l_name := last_names[1 + floor(random() * 20)::integer];
        
        -- Distribute customers evenly among the 5 countries
        country_idx := 1 + (i % 5);
        c_country := countries[country_idx];
        
        -- Pick city and state matching country
        geo_idx := 1 + floor(random() * 5)::integer;
        IF c_country = 'United States' THEN
            c_city := us_cities[geo_idx];
            s_state := us_states[geo_idx];
        ELSIF c_country = 'Canada' THEN
            c_city := ca_cities[geo_idx];
            s_state := ca_states[geo_idx];
        ELSIF c_country = 'United Kingdom' THEN
            c_city := uk_cities[geo_idx];
            s_state := uk_states[geo_idx];
        ELSIF c_country = 'Germany' THEN
            c_city := de_cities[geo_idx];
            s_state := de_states[geo_idx];
        ELSE -- Australia
            c_city := au_cities[geo_idx];
            s_state := au_states[geo_idx];
        END IF;
        
        created_ts := CURRENT_TIMESTAMP - (random() * 365 || ' days')::interval;
        
        INSERT INTO customers (first_name, last_name, email, city, state, country, created_at)
        VALUES (
            f_name, 
            l_name, 
            lower(f_name || '.' || l_name || '.' || i || '@global-telemetry.com'), 
            c_city, 
            s_state, 
            c_country,
            created_ts
        );
    END LOOP;
END
$$;

-- 3. Generate exactly 550 Orders and corresponding Order Items linking products and customers
DO $$
DECLARE
    v_order_id INTEGER;
    v_customer_id INTEGER;
    v_order_date TIMESTAMP WITH TIME ZONE;
    v_product_id INTEGER;
    v_quantity INTEGER;
    v_price NUMERIC(10, 2);
    v_order_total NUMERIC(10, 2);
    v_num_items INTEGER;
    v_cust_created TIMESTAMP WITH TIME ZONE;
BEGIN
    FOR i IN 1..550 LOOP
        -- Select a random customer between 1 and 100
        v_customer_id := 1 + floor(random() * 100)::integer;
        
        -- Make sure the order date occurs AFTER the customer account creation
        SELECT created_at INTO v_cust_created FROM customers WHERE customer_id = v_customer_id;
        v_order_date := v_cust_created + (random() * (EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - v_cust_created))) || ' seconds')::interval;
        
        -- Insert order header
        INSERT INTO orders (customer_id, order_date, total_amount)
        VALUES (v_customer_id, v_order_date, 0.00)
        RETURNING order_id INTO v_order_id;
        
        v_order_total := 0.00;
        
        -- Generate between 1 and 5 line items per order
        v_num_items := 1 + floor(random() * 5)::integer;
        
        FOR j IN 1..v_num_items LOOP
            -- Select a random product between 1 and 52
            v_product_id := 1 + floor(random() * 52)::integer;
            
            -- Fetch current product price
            SELECT price INTO v_price FROM products WHERE product_id = v_product_id;
            
            -- Determine random quantity (1 to 4)
            v_quantity := 1 + floor(random() * 4)::integer;
            
            -- Insert order item
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (v_order_id, v_product_id, v_quantity, v_price);
            
            v_order_total := v_order_total + (v_quantity * v_price);
        END LOOP;
        
        -- Update order total amount header
        UPDATE orders SET total_amount = v_order_total WHERE order_id = v_order_id;
    END LOOP;
END
$$;
