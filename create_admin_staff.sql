-- Add role column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='role') THEN
        ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'customer';
    END IF;
END $$;

-- Insert Admin Customer
INSERT INTO customers (id, first_name, last_name, address, city, state, zip_code, mobile, email, created_date, updated_date, created_by, updated_by)
VALUES (1000, 'Admin', 'User', 'Store HQ', 'Kothamangalam', 'Kerala', '686691', '1111111111', 'admin@ssms.com', NOW(), NOW(), 'system', 'system')
ON CONFLICT (mobile) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email;

-- Insert Admin User
INSERT INTO users (id, mobile, email, hashed_password, role, customer_id, created_date, updated_date, created_by, updated_by, created_at, updated_at)
VALUES ('admin-uuid-0001', '1111111111', 'admin@ssms.com', '$2b$12$3ufC/FzEuizOqPlPyisw0eHcJa4hxutCE1e4mtGKShnhmvdEyrVjK', 'admin', 1000, NOW(), NOW(), 'system', 'system', NOW(), NOW())
ON CONFLICT (mobile) DO UPDATE SET
    hashed_password = EXCLUDED.hashed_password,
    role = EXCLUDED.role,
    customer_id = EXCLUDED.customer_id;

-- Insert Staff Customer
INSERT INTO customers (id, first_name, last_name, address, city, state, zip_code, mobile, email, created_date, updated_date, created_by, updated_by)
VALUES (1001, 'Staff', 'User', 'Store branch', 'Kothamangalam', 'Kerala', '686691', '2222222222', 'staff@ssms.com', NOW(), NOW(), 'system', 'system')
ON CONFLICT (mobile) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email;

-- Insert Staff User
INSERT INTO users (id, mobile, email, hashed_password, role, customer_id, created_date, updated_date, created_by, updated_by, created_at, updated_at)
VALUES ('staff-uuid-0001', '2222222222', 'staff@ssms.com', '$2b$12$btWTW3lXwLXpos.Qcbb3tOO/sb5tojNCRN8y4mCYqwsC2G1LsduI6', 'staff', 1001, NOW(), NOW(), 'system', 'system', NOW(), NOW())
ON CONFLICT (mobile) DO UPDATE SET
    hashed_password = EXCLUDED.hashed_password,
    role = EXCLUDED.role,
    customer_id = EXCLUDED.customer_id;

-- Update sequence for customers
SELECT setval('customers_id_seq', (SELECT MAX(id) FROM customers));
