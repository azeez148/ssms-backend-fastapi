UPDATE public.products
SET
  name = concat('2025-26 ', name),
  description = concat('2025-26 ', description),
  updated_date = NOW(),
  updated_by = 'admin'
WHERE id BETWEEN 561 AND 685
  AND category_id = 1;
