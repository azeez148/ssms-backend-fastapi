-- Update logic for category id 1
UPDATE products
SET
    selling_price = 300,
    discounted_price = 250
WHERE
    category_id = 1
    AND unit_price = 165
    AND (discounted_price IS NULL OR discounted_price = 0)
    AND offer_id IS NULL;

UPDATE products
SET
    selling_price = 350,
    discounted_price = 300
WHERE
    category_id = 1
    AND unit_price = 195
    AND (discounted_price IS NULL OR discounted_price = 0)
    AND offer_id IS NULL;

UPDATE products
SET
    selling_price = 400,
    discounted_price = 350
WHERE
    category_id = 1
    AND unit_price = 215
    AND (discounted_price IS NULL OR discounted_price = 0)
    AND offer_id IS NULL;

-- Update logic for category id 2
UPDATE products
SET
    selling_price = 300,
    discounted_price = 250
WHERE
    category_id = 2
    AND unit_price = 165
    AND (discounted_price IS NULL OR discounted_price = 0)
    AND offer_id IS NULL;

UPDATE products
SET
    selling_price = 350,
    discounted_price = 300
WHERE
    category_id = 2
    AND unit_price = 195
    AND (discounted_price IS NULL OR discounted_price = 0)
    AND offer_id IS NULL;

UPDATE products
SET
    selling_price = 400,
    discounted_price = 350
WHERE
    category_id = 2
    AND unit_price = 215
    AND (discounted_price IS NULL OR discounted_price = 0)
    AND offer_id IS NULL;

-- Update logic for category id 3
UPDATE products
SET
    selling_price = 350,
    discounted_price = 300
WHERE
    category_id = 3
    AND unit_price = 195
    AND (discounted_price IS NULL OR discounted_price = 0)
    AND offer_id IS NULL;

UPDATE products
SET
    selling_price = 400,
    discounted_price = 350
WHERE
    category_id = 3
    AND unit_price >= 210
    AND (discounted_price IS NULL OR discounted_price = 0)
    AND offer_id IS NULL;

-- Update logic for category id 19
UPDATE products
SET
    selling_price = 600,
    discounted_price = 550
WHERE
    category_id = 19
    AND unit_price BETWEEN 280 AND 350
    AND (discounted_price IS NULL OR discounted_price = 0)
    AND offer_id IS NULL;

UPDATE products
SET
    selling_price = 700,
    discounted_price = 650
WHERE
    category_id = 19
    AND unit_price > 350
    AND (discounted_price IS NULL OR discounted_price = 0)
    AND offer_id IS NULL;

UPDATE products
SET
    selling_price = 500,
    discounted_price = 450
WHERE
    category_id = 19
    AND unit_price < 280
    AND (discounted_price IS NULL OR discounted_price = 0)
    AND offer_id IS NULL;
