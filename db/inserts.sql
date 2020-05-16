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

    INSERT INTO SensorsUnits (name, initial, precision, id_sensor, isdefault)
    VALUES	('Litro',               'l',    3, (SELECT id FROM Sensors WHERE name = Volume), 'TRUE'),
            ('Centimetro Cubico',   'cm^3', 3, (SELECT id FROM Sensors WHERE name = Volume), 'FALSE'),
    	    ('Metro Cubico',        'm^3',  3, (SELECT id FROM Sensors WHERE name = Volume), 'FALSE'),
	        ('Milimitro',           'mm',   2, (SELECT id FROM Sensors WHERE name = Distance), 'FALSE'),
	        ('Centimetro',          'cm',   2, (SELECT id FROM Sensors WHERE name = Distance), 'FALSE'),
	        ('Metro',               'm',    2, (SELECT id FROM Sensors WHERE name = Distance), 'TRUE'),
	        ('Kilometro',           'km',   2, (SELECT id FROM Sensors WHERE name = Distance), 'FALSE'),
	        ('Celsio',              'ºC',   2, (SELECT id FROM Sensors WHERE name = Temperature), 'TRUE'),
	        ('Farenhit',            'ºF',   2, (SELECT id FROM Sensors WHERE name = Temperature), 'FALSE'),
	        ('Kelvin',              'K',    2, (SELECT id FROM Sensors WHERE name = Temperature), 'FALSE'),
	        ('Grama',               'g',    3, (SELECT id FROM Sensors WHERE name = Mass), 'FALSE'),
	        ('Kilo',                'kg',   3, (SELECT id FROM Sensors WHERE name = Mass), 'TRUE'),
	        ('Tonelada',            't',    2, (SELECT id FROM Sensors WHERE name = Mass), 'FALSE'),
	        ('Segundo',             's',    3, (SELECT id FROM Sensors WHERE name = Time), 'TRUE'),
	        ('Minuto',              'min',  2, (SELECT id FROM Sensors WHERE name = Time), 'FALSE'),
	        ('Hora',                'h',    2, (SELECT id FROM Sensors WHERE name = Time), 'FALSE'),
	        ('Ampere',              'A',    2, (SELECT id FROM Sensors WHERE name = CurrentEletric), 'TRUE'),
	        ('Volts',               'V',    2, (SELECT id FROM Sensors WHERE name = EletricTension), 'TRUE'),
	        ('Lumens',              'lm',   2, (SELECT id FROM Sensors WHERE name = LightIntensity), 'TRUE'),
	        ('Gigapascal',          'GPa',  3, (SELECT id FROM Sensors WHERE name = Pressure), 'FALSE'),
	        ('Megapascal',          'MPa',  3, (SELECT id FROM Sensors WHERE name = Pressure), 'FALSE'),
	        ('Kilopascal',          'kPa',  3, (SELECT id FROM Sensors WHERE name = Pressure), 'FALSE'),
	        ('Pascal',              'Pa',   2, (SELECT id FROM Sensors WHERE name = Pressure), 'TRUE'),
	        ('Newton',              'N',    2, (SELECT id FROM Sensors WHERE name = Force), 'TRUE'),
	        ('Kilograma força',     'Kgf',  3, (SELECT id FROM Sensors WHERE name = Force), 'FALSE'),
            ('Watt',                'W',    2, (SELECT id FROM Sensors WHERE name = Power), 'TRUE'),
	        ('Miliwatt',            'mW',   3, (SELECT id FROM Sensors WHERE name = Power), 'FALSE'),
		    ('Ligado/Desligado',    NULL,   0, (SELECT id FROM Sensors WHERE name = State), 'FALSE'),
		    ('Aberto/Fechado',      NULL,   0, (SELECT id FROM Sensors WHERE name = State), 'FALSE'),
		    ('Decibeis',            'dB',   0, (SELECT id FROM Sensors WHERE name = Sound), 'TRUE');

END;
$$ LANGUAGE plpgsql;

