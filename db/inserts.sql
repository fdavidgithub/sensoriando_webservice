DO $$
DECLARE 
    Volume          VARCHAR := 'Volume';
    Distance        VARCHAR := 'Distância';
    Temperature     VARCHAR := 'Temperatura';
    Mass            VARCHAR := 'Massa';
    Time            VARCHAR := 'Tempo';
    CurrentEletric  VARCHAR := 'Corrente Elétrica';
    EletricTension  VARCHAR := 'Tensão Elétrica';
    LightIntensity  VARCHAR := 'Intensidade Luminosa';
    Pressure        VARCHAR := 'Pressão';
    Force           VARCHAR := 'Força';
    Power           VARCHAR := 'Potência';
BEGIN
    INSERT INTO Categories (name)
    VALUES	(Volume),
	        (Distance),
	        (Temperature),
	        (Mass),
	        (Time),
	        (CurrentEletric),
	        (EletricTension),
	        (LightIntensity),
	        (Pressure),
	        (Force),
            (Power);

    INSERT INTO Units (name, initial, precision, id_category)
    VALUES	('Litro',               'l',    3, (SELECT id FROM Categories WHERE name = Volume)),
            ('Centimetro Cubico',   'cm^3', 3, (SELECT id FROM Categories WHERE name = Volume)),
    	    ('Metro Cubico',        'm^3',  3, (SELECT id FROM Categories WHERE name = Volume)),
	        ('Milimitro',           'mm',   2, (SELECT id FROM Categories WHERE name = Distance)),
	        ('Centimetro',          'cm',   2, (SELECT id FROM Categories WHERE name = Distance)),
	        ('Metro',               'm',    2, (SELECT id FROM Categories WHERE name = Distance)),
	        ('Kilometro',           'km',   2, (SELECT id FROM Categories WHERE name = Distance)),
	        ('Celsio',              'ºC',   2, (SELECT id FROM Categories WHERE name = Temperature)),
	        ('Farenhit',            'ºF',   2, (SELECT id FROM Categories WHERE name = Temperature)),
	        ('Kelvin',              'K',    2, (SELECT id FROM Categories WHERE name = Temperature)),
	        ('Grama',               'g',    3, (SELECT id FROM Categories WHERE name = Mass)),
	        ('Kilo',                'kg',   3, (SELECT id FROM Categories WHERE name = Mass)),
	        ('Tonelada',            't',    2, (SELECT id FROM Categories WHERE name = Mass)),
	        ('Segundo',             's',    3, (SELECT id FROM Categories WHERE name = Time)),
	        ('Minuto',              'min',  2, (SELECT id FROM Categories WHERE name = Time)),
	        ('Hora',                'h',    2, (SELECT id FROM Categories WHERE name = Time)),
	        ('Ampere',              'A',    2, (SELECT id FROM Categories WHERE name = CurrentEletric)),
	        ('Volts',               'V',    2, (SELECT id FROM Categories WHERE name = EletricTension)),
	        ('Lumens',              'lm',   2, (SELECT id FROM Categories WHERE name = LightIntensity)),
	        ('Gigapascal',          'GPa',  3, (SELECT id FROM Categories WHERE name = Pressure)),
	        ('Megapascal',          'MPa',  3, (SELECT id FROM Categories WHERE name = Pressure)),
	        ('Kilopascal',          'kPa',  3, (SELECT id FROM Categories WHERE name = Pressure)),
	        ('Pascal',              'Pa',   2, (SELECT id FROM Categories WHERE name = Pressure)),
	        ('Newton',              'N',    2, (SELECT id FROM Categories WHERE name = Force)),
	        ('Kilograma força',     'Kgf',  3, (SELECT id FROM Categories WHERE name = Force)),
            ('Watt',                'W',    2, (SELECT id FROM Categories WHERE name = Power)),
	        ('Miliwatt',            'mW',   3, (SELECT id FROM Categories WHERE name = Power));

END;
$$ LANGUAGE plpgsql;

