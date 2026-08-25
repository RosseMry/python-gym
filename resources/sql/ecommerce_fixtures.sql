-- E-Commerce Sales Analysis Mini Project fixtures (Sprint 4 Mini
-- Project pilot - CON-29/30/31). A dedicated, self-contained dataset
-- and schema, deliberately NOT shared with the Foundations "fixtures"
-- schema (resources/sql/fixtures.sql) - a Mini Project's whole point
-- is one coherent dataset a learner progresses through across parts,
-- not a schema mixed with unrelated Foundations content.
--
-- Adapted from the source material's MySQL-flavored schema/data (INT
-- PRIMARY KEY, no sequences, VARCHAR) to real PostgreSQL (SERIAL,
-- proper FK ON DELETE behavior) - column/table names and the sample
-- rows themselves are kept as given, since that's the actual project
-- content, not something to redesign.
--
-- Loaded by scripts/provision_sql_fixtures.py alongside every other
-- resources/sql/*.sql file. Student submissions run inside a
-- transaction that is always rolled back (see
-- app/services/sql_execution_service.py), so this data is never
-- mutated by grading.

DROP SCHEMA IF EXISTS ecommerce_sales_analysis CASCADE;
CREATE SCHEMA ecommerce_sales_analysis;
SET search_path TO ecommerce_sales_analysis;

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name TEXT NOT NULL,
    gender TEXT NOT NULL,
    city TEXT NOT NULL,
    signup_date DATE NOT NULL
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers (customer_id),
    order_date DATE NOT NULL,
    order_status TEXT NOT NULL
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders (order_id),
    product_id INTEGER NOT NULL REFERENCES products (product_id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL
);

INSERT INTO customers (customer_id, customer_name, gender, city, signup_date) VALUES
    (1, 'Rahul', 'Male',   'Mumbai',    '2025-01-10'),
    (2, 'Priya', 'Female', 'Delhi',     '2025-01-15'),
    (3, 'Amit',  'Male',   'Pune',      '2025-02-01'),
    (4, 'Sneha', 'Female', 'Bangalore', '2025-02-10'),
    (5, 'Rohan', 'Male',   'Hyderabad', '2025-03-05');

INSERT INTO products (product_id, product_name, category, price) VALUES
    (101, 'Laptop',        'Electronics', 65000),
    (102, 'Headphones',    'Electronics', 2500),
    (103, 'Office Chair',  'Furniture',   7000),
    (104, 'Keyboard',      'Electronics', 1800),
    (105, 'Water Bottle',  'Home',        600);

INSERT INTO orders (order_id, customer_id, order_date, order_status) VALUES
    (1001, 1, '2025-03-01', 'Delivered'),
    (1002, 2, '2025-03-03', 'Delivered'),
    (1003, 1, '2025-03-10', 'Delivered'),
    (1004, 3, '2025-03-15', 'Cancelled'),
    (1005, 4, '2025-03-20', 'Delivered');

INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price) VALUES
    (1, 1001, 101, 1, 65000),
    (2, 1001, 102, 2, 2500),
    (3, 1002, 103, 1, 7000),
    (4, 1003, 104, 1, 1800),
    (5, 1004, 105, 3, 600),
    (6, 1005, 101, 1, 65000);

-- Explicit ids never advance the SERIAL sequences - see
-- resources/sql/fixtures.sql for why this matters for any exercise
-- that INSERTs a new row without specifying an id.
SELECT setval('customers_customer_id_seq', (SELECT max(customer_id) FROM customers));
SELECT setval('products_product_id_seq', (SELECT max(product_id) FROM products));
SELECT setval('orders_order_id_seq', (SELECT max(order_id) FROM orders));
SELECT setval(
    'order_items_order_item_id_seq',
    (SELECT max(order_item_id) FROM order_items)
);

RESET search_path;
