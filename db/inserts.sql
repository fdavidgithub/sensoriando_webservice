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
    State           VARCHAR := 'Estado';
    Sound           VARCHAR := 'Som';

BEGIN
    INSERT INTO Sensors (name)
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
            (Power),
		    (State),
            (Sound);

    INSERT INTO SensorsUnits (name, initial, precision, id_sensor)
    VALUES	('Litro',               'l',    3, (SELECT id FROM Sensors WHERE name = Volume)),
            ('Centimetro Cubico',   'cm^3', 3, (SELECT id FROM Sensors WHERE name = Volume)),
    	    ('Metro Cubico',        'm^3',  3, (SELECT id FROM Sensors WHERE name = Volume)),
	        ('Milimitro',           'mm',   2, (SELECT id FROM Sensors WHERE name = Distance)),
	        ('Centimetro',          'cm',   2, (SELECT id FROM Sensors WHERE name = Distance)),
	        ('Metro',               'm',    2, (SELECT id FROM Sensors WHERE name = Distance)),
	        ('Kilometro',           'km',   2, (SELECT id FROM Sensors WHERE name = Distance)),
	        ('Celsio',              'ºC',   2, (SELECT id FROM Sensors WHERE name = Temperature)),
	        ('Farenhit',            'ºF',   2, (SELECT id FROM Sensors WHERE name = Temperature)),
	        ('Kelvin',              'K',    2, (SELECT id FROM Sensors WHERE name = Temperature)),
	        ('Grama',               'g',    3, (SELECT id FROM Sensors WHERE name = Mass)),
	        ('Kilo',                'kg',   3, (SELECT id FROM Sensors WHERE name = Mass)),
	        ('Tonelada',            't',    2, (SELECT id FROM Sensors WHERE name = Mass)),
	        ('Segundo',             's',    3, (SELECT id FROM Sensors WHERE name = Time)),
	        ('Minuto',              'min',  2, (SELECT id FROM Sensors WHERE name = Time)),
	        ('Hora',                'h',    2, (SELECT id FROM Sensors WHERE name = Time)),
	        ('Ampere',              'A',    2, (SELECT id FROM Sensors WHERE name = CurrentEletric)),
	        ('Volts',               'V',    2, (SELECT id FROM Sensors WHERE name = EletricTension)),
	        ('Lumens',              'lm',   2, (SELECT id FROM Sensors WHERE name = LightIntensity)),
	        ('Gigapascal',          'GPa',  3, (SELECT id FROM Sensors WHERE name = Pressure)),
	        ('Megapascal',          'MPa',  3, (SELECT id FROM Sensors WHERE name = Pressure)),
	        ('Kilopascal',          'kPa',  3, (SELECT id FROM Sensors WHERE name = Pressure)),
	        ('Pascal',              'Pa',   2, (SELECT id FROM Sensors WHERE name = Pressure)),
	        ('Newton',              'N',    2, (SELECT id FROM Sensors WHERE name = Force)),
	        ('Kilograma força',     'Kgf',  3, (SELECT id FROM Sensors WHERE name = Force)),
            ('Watt',                'W',    2, (SELECT id FROM Sensors WHERE name = Power)),
	        ('Miliwatt',            'mW',   3, (SELECT id FROM Sensors WHERE name = Power)),
		    ('Ligado/Desligado',    NULL,   0, (SELECT id FROM Sensors WHERE name = State)),
		    ('Aberto/Fechado',      NULL,   0, (SELECT id FROM Sensors WHERE name = State)),
		    ('Decibeis',            'dB',   0, (SELECT id FROM Sensors WHERE name = Sound));


    INSERT INTO Accounts (city, uf) 
    VALUES ('Ribeirao Preto', 'SP');

    INSERT INTO Things (name)
    VALUES ('THING_TEST');

END;
$$ LANGUAGE plpgsql;

