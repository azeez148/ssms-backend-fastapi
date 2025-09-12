INSERT INTO public.delivery_types(
	id, name, description, charge)
	VALUES
        (1, 'Pickup from Store', 'Customer picks up the order from the store', 0),
        (2, 'PO-Standard Delivery', 'Delivery within 3-5 business days', 50),
        (3, 'PO-Express Delivery', 'Delivery within 1-3 business days', 65),
        (4, 'DTDC/SS Delivery', 'Delivery through DTDC or SS courier service', 75);