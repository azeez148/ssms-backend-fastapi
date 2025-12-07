-- Reset product IDs before inserting (optional if table is not empty)
-- TRUNCATE TABLE public.products RESTART IDENTITY;

INSERT INTO public.products
(id, name, description, unit_price, selling_price, is_active, can_listed, image_url, category_id, offer_id, discounted_price, offer_price, offer_name, created_date, updated_date, created_by, updated_by)
VALUES

-- *********************
-- ***** FIVESLEEVE *****
-- Category_id = 3
-- Premium price triggers: Collar / Embroidery / Button
-- *********************

(698, 'FC Barcelona White Collar 125th Anniversary Cruyff', 'FC Barcelona White Collar 125th Anniversary Cruyff', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(699, 'FC Barcelona 2004–05 Home Ronaldinho 10 Embroidery', 'FC Barcelona 2004–05 Home Ronaldinho 10 Embroidery', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(700, 'Germany 2024–25 Training Lahm 16', 'Germany 2024–25 Training Lahm 16', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(701, 'Germany 2024–25 Training Özil 8', 'Germany 2024–25 Training Özil 8', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(702, 'FC Barcelona x Travis Scott Home', 'FC Barcelona x Travis Scott Home', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(703, 'FC Barcelona White Collar Button Embroidery', 'FC Barcelona White Collar Button Embroidery', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(704, 'Atlético Madrid Home Collar With Button', 'Atlético Madrid Home Collar With Button', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(705, 'Liverpool FC 1993 Away Carlsberg Torres', 'Liverpool FC 1993 Away Carlsberg Torres', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(706, 'England 1998 World Cup Umbro White Collar White V-Neck', 'England 1998 World Cup Umbro White Collar White V-Neck', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(707, 'Real Madrid 1997–98 Kelme Away Purple Collar With Button Carlos', 'Real Madrid 1997–98 Kelme Away Purple Collar With Button Carlos', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(708, 'Sporting CP 1998–99 Away CR7 Collar White and Green', 'Sporting CP 1998–99 Away CR7 Collar White and Green', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(709, 'Germany 1998–2000 Klinsmann Green and White Collar', 'Germany 1998–2000 Klinsmann Green and White Collar', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(710, 'AC Milan 1998–99 Home Maldini 3 Collar', 'AC Milan 1998–99 Home Maldini 3 Collar', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(711, 'Liverpool FC 1995–96 Green Black and White Training', 'Liverpool FC 1995–96 Green Black and White Training', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(712, 'Juventus US Pack Baseball Jersey White and Black Lines', 'Juventus US Pack Baseball Jersey White and Black Lines', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(713, 'Germany 1990 Special Kit Beckenbauer Fivesleeve Collar', 'Germany 1990 Special Kit Beckenbauer Fivesleeve Collar', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(714, 'AC Milan 1997–98 Fourth Kit Maldini 3 Opel', 'AC Milan 1997–98 Fourth Kit Maldini 3 Opel', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(715, 'Inter Milan 2004–05 Nike Training R9', 'Inter Milan 2004–05 Nike Training R9', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(716, 'Bayern Munich 2002–03 Home Ballack 13', 'Bayern Munich 2002–03 Home Ballack 13', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(717, 'Fiorentina 1999–2000 Home Collar Batistuta', 'Fiorentina 1999–2000 Home Collar Batistuta', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(718, 'Arsenal FC 2017–18 Third Collar Black Özil 11', 'Arsenal FC 2017–18 Third Collar Black Özil 11', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(719, 'Real Madrid 2017–18 Third CR7', 'Real Madrid 2017–18 Third CR7', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(720, 'Real Madrid 2003–04 Away Blue Siemens Carlos', 'Real Madrid 2003–04 Away Blue Siemens Carlos', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(721, 'Italy 1996–97 Away White Baggio 10', 'Italy 1996–97 Away White Baggio 10', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(722, 'Italy Away 2015–16 White Pirlo 21', 'Italy Away 2015–16 White Pirlo 21', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(723, 'Real Madrid 2017 Away Purple CR7', 'Real Madrid 2017 Away Purple CR7', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(724, 'Manchester United 1999 Home Collar Sharp Beckham 7', 'Manchester United 1999 Home Collar Sharp Beckham 7', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(725, 'Real Madrid 2011–12 Home Collar CR7', 'Real Madrid 2011–12 Home Collar CR7', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(726, 'Liverpool 2011–12 Training White Torres', 'Liverpool 2011–12 Training White Torres', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(727, 'England 2004 Home David Beckham White', 'England 2004 Home David Beckham White', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(728, 'Germany 1990 Rummenigge Embroidery', 'Germany 1990 Rummenigge Embroidery', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(729, 'Liverpool Away 1996–97 V-Neck Collar Cream Gerrard 8', 'Liverpool Away 1996–97 V-Neck Collar Cream Gerrard 8', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(730, 'Atlético Madrid 2016–17 Home Torres', 'Atlético Madrid 2016–17 Home Torres', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(731, 'Wolves 1996–98 Home Yellow No. 10', 'Wolves 1996–98 Home Yellow No. 10', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(732, 'FC Barcelona 2015–16 Home Messi 10', 'FC Barcelona 2015–16 Home Messi 10', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(733, 'Liverpool FC 2010–11 Home Gerrard 8', 'Liverpool FC 2010–11 Home Gerrard 8', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(734, 'Manchester United 1992–94 Third Yellow Green Collar Beckham', 'Manchester United 1992–94 Third Yellow Green Collar Beckham', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(735, 'Argentina Special Edition Kit Batistuta Embroidery', 'Argentina Special Edition Kit Batistuta Embroidery', 215, 375, TRUE, TRUE, NULL, 3, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(736, 'England Home 1982 Beckham 7', 'England Home 1982 Beckham 7', 195, 350, TRUE, TRUE, NULL, 3, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),

-- *****************************
-- ***** NORMAL SLEEVE RETRO *****
-- Category_id = 1
-- Pricing: 195/165 unit | 350/300 selling | 300/250 discounted
-- *****************************

(737, 'Real Madrid 1999–2000 Home White Beckham 23', 'Real Madrid 1999–2000 Home White Beckham 23', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(738, 'Real Madrid 2017–18 Third Sky Blue CR7', 'Real Madrid 2017–18 Third Sky Blue CR7', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(739, 'Real Madrid 2016–17 Away Purple Sergio Ramos', 'Real Madrid 2016–17 Away Purple Sergio Ramos', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(740, 'AC Milan 2014–15 Home Kaka 22', 'AC Milan 2014–15 Home Kaka 22', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(741, 'Portugal Away 2016 Green CR7', 'Portugal Away 2016 Green CR7', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(742, 'Real Madrid 2011–12 Home Collar Embroidery', 'Real Madrid 2011–12 Home Collar Embroidery', 195, 350, TRUE, TRUE, NULL, 1, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(743, 'Real Madrid 2012–13 Home Bwin CR7', 'Real Madrid 2012–13 Home Bwin CR7', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(744, 'AC Milan 2024–25 Away Collar Kaka 22', 'AC Milan 2024–25 Away Collar Kaka 22', 195, 350, TRUE, TRUE, NULL, 1, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(745, 'Inter Milan 2009–10 Home Ibrahimović', 'Inter Milan 2009–10 Home Ibrahimović', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(746, 'FC Barcelona 2019–20 Away Yellow Rakuten Messi', 'FC Barcelona 2019–20 Away Yellow Rakuten Messi', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(747, 'Real Madrid Third 2012–13 Green CR7', 'Real Madrid Third 2012–13 Green CR7', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(748, 'Manchester United 2007–08 Black Away AIG CR7', 'Manchester United 2007–08 Black Away AIG CR7', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(749, 'FC Bayern Munich 2024–25 Away Kroos', 'FC Bayern Munich 2024–25 Away Kroos', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(750, 'Manchester United 2007–08 Home CR7', 'Manchester United 2007–08 Home CR7', 165, 300, TRUE, TRUE, NULL, 1, NULL, 250, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),

-- *****************************
-- ***** FULL SLEEVE ************
-- Category_id = 2
-- Pricing: 215/195 unit | 375/350 selling | 350/300 discount
-- *****************************

(751, 'Bayern Munich 2000–02 Away Embroidery Matthäus', 'Bayern Munich 2000–02 Away Embroidery Matthäus', 215, 375, TRUE, TRUE, NULL, 2, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(752, 'Manchester United 2001–02 Away Embroidery Beckham 7', 'Manchester United 2001–02 Away Embroidery Beckham 7', 215, 375, TRUE, TRUE, NULL, 2, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(753, 'Liverpool Away 1993–95 Embroidery Torres 9', 'Liverpool Away 1993–95 Embroidery Torres 9', 215, 375, TRUE, TRUE, NULL, 2, NULL, 350, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(754, 'Manchester United 2008–09 Away CR7', 'Manchester United 2008–09 Away CR7', 195, 350, TRUE, TRUE, NULL, 2, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(755, 'Manchester United 2007–08 Away Black CR7', 'Manchester United 2007–08 Away Black CR7', 195, 350, TRUE, TRUE, NULL, 2, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(756, 'FC Barcelona 2008–09 Home Messi', 'FC Barcelona 2008–09 Home Messi', 195, 350, TRUE, TRUE, NULL, 2, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin'),
(757, 'AC Milan 2006–07 Away Kaka 22', 'AC Milan 2006–07 Away Kaka 22', 195, 350, TRUE, TRUE, NULL, 2, NULL, 300, NULL, NULL, NOW(), NOW(), 'admin', 'admin');

-- Reset Postgres sequence
SELECT setval('products_id_seq', (SELECT MAX(id) FROM products));
