INSERT INTO Category (name)
VALUES	('Volume'),
	('Distância'),
	('Temperatura'),
	('Massa'),
	('Tempo'),
	('Corrente Elétrica'),
	('Tensão Elétrica'),
	('Intensidade Luminosa'),
	('Pressão'),
	('Força');


INSERT INTO Unit (name, initial, precision, id_category)
VALUES	('Litro', 'l', 3, (SELECT id FROM Category WHERE name = 'Volume')),
      	('Centimetro Cubico', 'cm^3', 3, (SELECT id FROM Category WHERE name = 'Volume')),
	('Metro Cubico', 'm^3', 3, (SELECT id FROM Category WHERE name = 'Volume')),

	('Milimitro', 'mm', 2, (SELECT id FROM Category WHERE name = 'Distância')),
	('Centimetro', 'cm', 2, (SELECT id FROM Category WHERE name = 'Distância')),
	('Metro', 'm', 2, (SELECT id FROM Category WHERE name = 'Distância')),
	('Kilometro', 'km', 2, (SELECT id FROM Category WHERE name = 'Temperatura')),

	('Celsio', 'ºC', 2, (SELECT id FROM Category WHERE name = 'Temperatura')),
	('Farenhit', 'ºF', 2, (SELECT id FROM Category WHERE name = 'Temperatura')),
	('Kelvin', 'K', 2, (SELECT id FROM Category WHERE name = 'Temperatura')),

	('Grama', 'g', 3, (SELECT id FROM Category WHERE name = 'Massa')),
	('Kilo', 'kg', 3, (SELECT id FROM Category WHERE name = 'Massa')),
	('Tonelada', 't', 2, (SELECT id FROM Category WHERE name = 'Massa')),

	('Segundo', 's', 3, (SELECT id FROM Category WHERE name = 'Tempo')),
	('Minuto', 'min', 2, (SELECT id FROM Category WHERE name = 'Tempo')),
	('Hora', 'h', 2, (SELECT id FROM Category WHERE name = 'Tempo')),

	('Ampere', 'A', 2, (SELECT id FROM Category WHERE name = 'Corrente Elétrica')),

	('Volts', 'V', 2, (SELECT id FROM Category WHERE name = 'Tensão Elétrica')),

	('Lumens', 'cd', 2, (SELECT id FROM Category WHERE name = 'Intensidade Luminosa')),

	('Gigapascal', 'GPa', 3, (SELECT id FROM Category WHERE name = 'Pressão')),
	('Megapascal', 'MPa', 3, (SELECT id FROM Category WHERE name = 'Pressão')),
	('Kilopascal', 'kPa', 3, (SELECT id FROM Category WHERE name = 'Pressão')),
	('Pascal', 'Pa', 2,  (SELECT id FROM Category WHERE name = 'Pressão')),
	
	('Newton', 'N', 2, (SELECT id FROM Category WHERE name = 'Força')),
	('Kilograma força', 'Kgf', 3, (SELECT id FROM Category WHERE name = 'Força'));

