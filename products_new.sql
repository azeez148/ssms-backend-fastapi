INSERT INTO public.products 
(id, name, description, unit_price, selling_price, is_active, can_listed, image_url, category_id, offer_id, discounted_price, offer_price, offer_name, created_date, updated_date, created_by, updated_by) 
VALUES
(780, 'Manchester City 1999-2000 Home Aguero Blue Collar', 'Manchester City 1999-2000 Home Aguero Blue Collar', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(781, '1994-96 Real Madrid Kelme Zidane 5 Purple Collar', '1994-96 Real Madrid Kelme Zidane 5 Purple Collar', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(782, 'England 2004 Home White David Beckham Collar', 'England 2004 Home White David Beckham Collar', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(783, '1998-99 Manchester United Away Sharp David Beckham Embroidery V-Neck Collar', '1998-99 Manchester United Away Sharp David Beckham Embroidery V-Neck Collar', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(784, 'Barcelona 1999 Home Messi 19 Collar', 'Barcelona 1999 Home Messi 19 Collar', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(785, 'Real Madrid 3rd CR7 Dragon Jersey 2014 Black V-Neck Collar', 'Real Madrid 3rd CR7 Dragon Jersey 2014 Black V-Neck Collar', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(786, 'AC Milan 1999/2000 Away Black Open Maldini 3 V-Neck Collar', 'AC Milan 1999/2000 Away Black Open Maldini 3 V-Neck Collar', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(787, 'Real Madrid 1997–98 Kelme Away Purple Carlos', 'Real Madrid 1997–98 Kelme Away Purple Carlos', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(788, 'Athletic Sports White Blue No22', 'Athletic Sports White Blue No22', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(789, 'Italy 2016 Away Kit Maldini 3 Embroidery V-Neck Collar', 'Italy 2016 Away Kit Maldini 3 Embroidery V-Neck Collar', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(790, 'Germany 1996 Black And White Ballack 13 Embroidery V-Neck Collar', 'Germany 1996 Black And White Ballack 13 Embroidery V-Neck Collar', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(791, 'France 1996 Away Zidane 10', 'France 1996 Away Zidane 10', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(792, 'AC Milan 2005-06 Third Zafira Van Basten 10 Embroidery', 'AC Milan 2005-06 Third Zafira Van Basten 10 Embroidery', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(793, 'Manchester United 1996-98 Home Umbro White Collar Beckham', 'Manchester United 1996-98 Home Umbro White Collar Beckham', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(794, 'Chelsea 2007/2008 Third White Drogba 11 Embroidery', 'Chelsea 2007/2008 Third White Drogba 11 Embroidery', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),

-- Normal
(795, 'Ozil Arsenal Home Kit 2017 Polo Collar', 'Ozil Arsenal Home Kit 2017 Polo Collar', 195, 350, TRUE, TRUE, NULL, 1, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(796, 'Manchester United 97-98 Sharp Blue Beckham 10', 'Manchester United 97-98 Sharp Blue Beckham 10', 195, 350, TRUE, TRUE, NULL, 1, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(797, 'France 1996 Home Kit Zidane Polo Collar Tie', 'France 1996 Home Kit Zidane Polo Collar Tie', 195, 350, TRUE, TRUE, NULL, 1, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),

-- FS
(798, 'France 2006 Zidane 10 Away White Embroidery', 'France 2006 Zidane 10 Away White Embroidery', 215, 375, TRUE, TRUE, NULL, 2, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin');

-- Reset sequence
SELECT setval('products_id_seq', (SELECT MAX(id) FROM products));
