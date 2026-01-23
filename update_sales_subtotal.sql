-- Update sub_total in sales table based on product selling prices
UPDATE sales
SET sub_total = (
    SELECT COALESCE(SUM(COALESCE(p.selling_price, si.sale_price, 0) * si.quantity), 0)
    FROM sale_items si
    LEFT JOIN products p ON si.product_id = p.id
    WHERE si.sale_id = sales.id
);
