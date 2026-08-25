-- Python-Gym SQL exercise fixtures (Sprint 4).
--
-- A small, realistic relational dataset - departments/employees (with
-- a self-referential manager_id for hierarchy queries), customers/
-- products/orders/order_items (a real many-to-many via a junction
-- table), and appointments (a business-domain table distinct from the
-- e-commerce tables, for variety). Lives in its own "fixtures" schema
-- so it's never confused with the grading system's own tables.
--
-- Loaded once by scripts/provision_sql_fixtures.py. Student
-- submissions run inside a transaction that is always rolled back
-- (see app/services/sql_execution_service.py), so this data is never
-- mutated by grading, even by a submission that runs DELETE or DROP.

DROP SCHEMA IF EXISTS fixtures CASCADE;
CREATE SCHEMA fixtures;
SET search_path TO fixtures;

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    department_id INTEGER REFERENCES departments (id),
    manager_id INTEGER REFERENCES employees (id),
    salary NUMERIC(10, 2) NOT NULL,
    hire_date DATE NOT NULL
);

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    signup_date DATE NOT NULL
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers (id),
    order_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE order_items (
    order_id INTEGER NOT NULL REFERENCES orders (id),
    product_id INTEGER NOT NULL REFERENCES products (id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (order_id, product_id)
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers (id),
    employee_id INTEGER NOT NULL REFERENCES employees (id),
    appointment_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'scheduled'
);

INSERT INTO departments (id, name) VALUES
    (1, 'Engineering'),
    (2, 'Sales'),
    (3, 'Support'),
    (4, 'Marketing'),
    (5, 'Facilities');

-- Hedy has no department (department_id NULL) and Facilities has no
-- employees - a deliberate pair of orphans on both sides of the FK, so
-- JOIN exercises (RIGHT/FULL OUTER) have real unmatched rows to show.
INSERT INTO employees (id, first_name, last_name, department_id, manager_id, salary, hire_date) VALUES
    (1, 'Ada',     'Lovelace',  1, NULL, 9500.00, '2019-03-01'),
    (2, 'Alan',    'Turing',    1, 1,    8800.00, '2020-06-15'),
    (3, 'Grace',   'Hopper',    1, 1,    8600.00, '2021-01-11'),
    (4, 'Margaret','Hamilton',  2, NULL, 7200.00, '2018-09-20'),
    (5, 'Katherine','Johnson',  2, 4,    6100.00, '2022-02-01'),
    (6, 'Radia',   'Perlman',   3, NULL, 5900.00, '2020-11-05'),
    (7, 'Barbara', 'Liskov',    3, 6,    5400.00, '2023-04-18'),
    (8, 'Hedy',    'Lamarr',    NULL, NULL, 6800.00, '2021-07-30');

INSERT INTO customers (id, first_name, last_name, email, city, country, signup_date) VALUES
    (1,  'Ana',    'Silva',    'ana.silva@example.com',    'Lisbon',    'Portugal', '2022-01-15'),
    (2,  'Bo',     'Chen',     'bo.chen@example.com',      'Shanghai',  'China',    '2022-03-02'),
    (3,  'Cid',    'Rocha',    'cid.rocha@example.com',    'Porto',     'Portugal', '2022-05-19'),
    (4,  'Dara',   'Ola',      'dara.ola@example.com',     'Lagos',     'Nigeria',  '2022-07-08'),
    (5,  'Eero',   'Salo',     'eero.salo@example.com',    'Helsinki',  'Finland',  '2022-09-23'),
    (6,  'Fatima', 'Haidari',  'fatima.h@example.com',     'Kabul',     'Afghanistan', '2023-01-30'),
    (7,  'Gustav', 'Berg',     'gustav.berg@example.com',  'Stockholm', 'Sweden',   '2023-02-14'),
    (8,  'Hana',   'Kobayashi','hana.k@example.com',       'Osaka',     'Japan',    '2023-04-11'),
    (9,  'Ivo',    'Novak',    'ivo.novak@example.com',    'Prague',    'Czechia',  '2023-06-27'),
    (10, 'Julia',  'Kowalski', 'julia.k@example.com',      'Warsaw',    'Poland',   '2023-08-05');

INSERT INTO products (id, name, category, price, stock_quantity) VALUES
    (1, 'Wireless Mouse',    'Electronics', 19.99, 150),
    (2, 'Mechanical Keyboard','Electronics', 79.99, 60),
    (3, 'USB-C Hub',         'Electronics', 34.50, 90),
    (4, 'Notebook A5',       'Stationery',   4.25, 400),
    (5, 'Fountain Pen',      'Stationery',  15.00, 120),
    (6, 'Desk Lamp',         'Home',        27.75, 75),
    (7, 'Standing Mat',      'Home',        45.00, 40),
    (8, 'Water Bottle',      'Home',        12.90, 200);

INSERT INTO orders (id, customer_id, order_date, status) VALUES
    (1,  1, '2023-09-01', 'shipped'),
    (2,  2, '2023-09-03', 'shipped'),
    (3,  1, '2023-09-10', 'shipped'),
    (4,  3, '2023-09-12', 'pending'),
    (5,  4, '2023-09-15', 'shipped'),
    (6,  5, '2023-09-18', 'cancelled'),
    (7,  6, '2023-09-20', 'shipped'),
    (8,  2, '2023-09-22', 'pending'),
    (9,  7, '2023-09-25', 'shipped'),
    (10, 8, '2023-09-27', 'shipped');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 2, 19.99),
    (1, 4, 3, 4.25),
    (2, 2, 1, 79.99),
    (3, 3, 1, 34.50),
    (3, 8, 2, 12.90),
    (4, 5, 4, 15.00),
    (5, 6, 1, 27.75),
    (5, 7, 1, 45.00),
    (7, 2, 1, 79.99),
    (7, 3, 1, 34.50),
    (8, 4, 10, 4.25),
    (9, 8, 3, 12.90),
    (10, 6, 2, 27.75);

INSERT INTO appointments (id, customer_id, employee_id, appointment_date, status) VALUES
    (1, 1, 6, '2023-10-02', 'completed'),
    (2, 2, 7, '2023-10-03', 'completed'),
    (3, 3, 6, '2023-10-05', 'no_show'),
    (4, 4, 7, '2023-10-06', 'completed'),
    (5, 5, 6, '2023-10-10', 'scheduled'),
    (6, 6, 7, '2023-10-11', 'scheduled'),
    (7, 1, 6, '2023-10-12', 'cancelled');

-- Every table above was seeded with explicit id values, which never
-- advances a SERIAL column's underlying sequence - without this, the
-- first plain INSERT (no id given) in any exercise would collide with
-- an existing row instead of continuing after it.
SELECT setval('departments_id_seq', (SELECT max(id) FROM departments));
SELECT setval('employees_id_seq', (SELECT max(id) FROM employees));
SELECT setval('customers_id_seq', (SELECT max(id) FROM customers));
SELECT setval('products_id_seq', (SELECT max(id) FROM products));
SELECT setval('orders_id_seq', (SELECT max(id) FROM orders));
SELECT setval('appointments_id_seq', (SELECT max(id) FROM appointments));

-- A real, always-present view - so a "DROP this view" exercise has
-- something genuine to remove, instead of a view a student just
-- created themselves in the same submission (which a no-op submission
-- would trivially "pass" too, since it was never there either way).
CREATE VIEW department_headcounts AS
    SELECT department_id, COUNT(*) AS headcount
    FROM employees
    WHERE department_id IS NOT NULL
    GROUP BY department_id;

-- Same reasoning as the view above, for a "DROP this index" exercise.
CREATE INDEX idx_products_category ON products (category);

-- Same reasoning again, for a "DROP this function" exercise.
CREATE FUNCTION full_name(first_name TEXT, last_name TEXT) RETURNS TEXT AS $$
BEGIN
    RETURN first_name || ' ' || last_name;
END;
$$ LANGUAGE plpgsql;

-- Same reasoning again, for a "DROP this procedure" exercise.
CREATE PROCEDURE mark_appointment_completed(appointment_id INTEGER) LANGUAGE plpgsql AS $$
BEGIN
    UPDATE appointments SET status = 'completed' WHERE id = appointment_id;
END;
$$;

-- Same reasoning again, for a "DROP this trigger" exercise. Deliberately
-- named apart from sql-triggers-01's own trigger/function so that
-- exercise's CREATE TRIGGER never collides with this one.
CREATE FUNCTION noop_order_trigger() RETURNS TRIGGER AS $$
BEGIN
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_touch_orders
    AFTER UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION noop_order_trigger();

RESET search_path;
