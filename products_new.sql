-- INSERT INTO public.products
-- (id, name, description, unit_price, selling_price, is_active, can_listed, image_url, category_id, offer_id, discounted_price, offer_price, offer_name, created_date, updated_date, created_by, updated_by)
-- VALUES
-- (811, 'Chelsea 2011-12 Away Torres 9', 'Chelsea 2011-12 Away Torres 9', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (812, 'Brazil Home Special Edition Ronaldinho 10 Dinho', 'Brazil Home Special Edition Ronaldinho 10 Dinho', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (813, 'France Home Special Edition Zidane 10 Zizou', 'France Home Special Edition Zidane 10 Zizou', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (814, 'England Home Special Edition Beckham 7 Beckz', 'England Home Special Edition Beckham 7 Beckz', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (815, 'Real Madrid 2020-21 Third Kroos Black And Pink Lines', 'Real Madrid 2020-21 Third Kroos Black And Pink Lines', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (816, 'Parma 1995-96 Away Collar Cannavaro', 'Parma 1995-96 Away Collar Cannavaro', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (817, 'Inter Milan Umbro Blue And Black Polo Collar Ronaldo 10', 'Inter Milan Umbro Blue And Black Polo Collar Ronaldo 10', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (818, 'Real Madrid 1997 White Beckham 23 Collar', 'Real Madrid 1997 White Beckham 23 Collar', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (819, 'Real Madrid 2007-08 Third Black And Green Raul 7', 'Real Madrid 2007-08 Third Black And Green Raul 7', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (820, 'Beckham Manchester United Away Kit 1997-98 Collar Sharp Embroidery', 'Beckham Manchester United Away Kit 1997-98 Collar Sharp Embroidery', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (821, 'Portugal 2025-26 Special Edition Eusebio Collar', 'Portugal 2025-26 Special Edition Eusebio Collar', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (822, 'Valley Blue And White No 33', 'Valley Blue And White No 33', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (823, 'France Fantasy Jersey Zidane Five Sleeve', 'France Fantasy Jersey Zidane Five Sleeve', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (824, 'Ferrari Black', 'Ferrari Black', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (825, 'England Away Umbro Blue Gerrard 4 Collar', 'England Away Umbro Blue Gerrard 4 Collar', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (826, 'AC Milan 1990-1992 Home Van Basten Collar Embroidery', 'AC Milan 1990-1992 Home Van Basten Collar Embroidery', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (827, 'Arsenal 2014-15 Home Ozil 11 Embroidery', 'Arsenal 2014-15 Home Ozil 11 Embroidery', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),

-- (828, 'Germany 2006 Home Ballack 13', 'Germany 2006 Home Ballack 13', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (829, 'AC Milan 2006-07 Home Paolo Maldini 3', 'AC Milan 2006-07 Home Paolo Maldini 3', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (830, 'Arsenal 2009-10 Away Van Persie Embroidery Collar', 'Arsenal 2009-10 Away Van Persie Embroidery Collar', 195, 350, TRUE, TRUE, NULL, 1, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (831, 'Portugal 2025-26 Away Black CR7', 'Portugal 2025-26 Away Black CR7', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (832, 'Germany 2014 Away Kroos 18', 'Germany 2014 Away Kroos 18', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (833, 'Real Madrid 2011-12 Home Ramos Embroidery Collar', 'Real Madrid 2011-12 Home Ramos Embroidery Collar', 195, 350, TRUE, TRUE, NULL, 1, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (834, 'Barcelona 2015-16 Home Neymar 11', 'Barcelona 2015-16 Home Neymar 11', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
-- (835, 'Manchester City 2025-26 Fourth Haaland', 'Manchester City 2025-26 Fourth Haaland', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin');

-- SELECT setval('products_id_seq', (SELECT MAX(id) FROM products));

SELECT id, name, unit_price, selling_price FROM public.products WHERE id >= 811 LIMIT 10;