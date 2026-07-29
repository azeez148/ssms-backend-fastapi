UPDATE public.products
SET category_id = 1
WHERE category_id = 3
  AND id NOT IN (18, 19, 20, 21);
