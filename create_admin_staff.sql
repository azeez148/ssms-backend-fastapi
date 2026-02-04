-- Add role column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='role') THEN
        ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'customer';
    END IF;
END $$;

-- Insert Admin Customer
INSERT INTO customers (id, first_name, last_name, address, city, state, zip_code, mobile, email, created_date, updated_date, created_by, updated_by)
VALUES (1000, 'Admin', 'User', 'Store HQ', 'Kothamangalam', 'Kerala', '686691', '7736128108', 'adrenalinesportsstore44@gmail.com', NOW(), NOW(), 'system', 'system')
ON CONFLICT (mobile) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email;

-- Insert Admin User
INSERT INTO users (id, mobile, email, hashed_password, role, customer_id, created_date, updated_date, created_by, updated_by, created_at, updated_at)
VALUES ('admin-uuid-0001', '7736128108', 'adrenalinesportsstore44@gmail.com', '7736128108', 'admin', 1000, NOW(), NOW(), 'system', 'system', NOW(), NOW())
ON CONFLICT (mobile) DO UPDATE SET
    hashed_password = EXCLUDED.hashed_password,
    role = EXCLUDED.role,
    customer_id = EXCLUDED.customer_id;

-- Insert Staff Customer
INSERT INTO customers (id, first_name, last_name, address, city, state, zip_code, mobile, email, created_date, updated_date, created_by, updated_by)
VALUES (1001, 'Staff', 'User', 'NKY', 'Kothamangalam', 'Kerala', '686691', '8943285336', 'staff.nky@ssms.com', NOW(), NOW(), 'system', 'system')
ON CONFLICT (mobile) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email;

-- Insert Staff User
INSERT INTO users (id, mobile, email, hashed_password, role, customer_id, created_date, updated_date, created_by, updated_by, created_at, updated_at)
VALUES ('staff-uuid-0001', '8943285336', 'staff.nky@ssms.com', '8943285336', 'staff', 1001, NOW(), NOW(), 'system', 'system', NOW(), NOW())
ON CONFLICT (mobile) DO UPDATE SET
    hashed_password = EXCLUDED.hashed_password,
    role = EXCLUDED.role,
    customer_id = EXCLUDED.customer_id;

-- Update sequence for customers
SELECT setval('customers_id_seq', (SELECT MAX(id) FROM customers));
