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
    Sound           VARCHAR := 'Som';
    State           VARCHAR := 'Estado';
    Message         VARCHAR := 'Mensagem';
    Humidity        VARCHAR := 'Umidade';

BEGIN
    INSERT INTO Sensors (name)
    VALUES	(Message),
            (Volume),
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
            (Sound),
            (State)
            (Humidity);

    INSERT INTO SensorsUnits (name, initial, precision, id_sensor, isdefault, expression)
    VALUES	('Litro',               'l',    3, (SELECT id FROM Sensors WHERE name = Volume), 'TRUE', 'pv'),
            ('Centimetro Cubico',   'cm^3', 3, (SELECT id FROM Sensors WHERE name = Volume), 'FALSE', 'pv * 1000'),
    	    ('Metro Cubico',        'm^3',  3, (SELECT id FROM Sensors WHERE name = Volume), 'FALSE', 'pv / 1000'),
	        ('Milimitro',           'mm',   2, (SELECT id FROM Sensors WHERE name = Distance), 'FALSE', 'pv * 1000'),
	        ('Centimetro',          'cm',   2, (SELECT id FROM Sensors WHERE name = Distance), 'FALSE', 'pv * 100'),
	        ('Metro',               'm',    2, (SELECT id FROM Sensors WHERE name = Distance), 'TRUE', 'pv'),
	        ('Kilometro',           'km',   2, (SELECT id FROM Sensors WHERE name = Distance), 'FALSE', 'pv / 1000'),
	        ('Celsio',              'ºC',   2, (SELECT id FROM Sensors WHERE name = Temperature), 'TRUE', 'pv'),
	        ('Farenhit',            'ºF',   2, (SELECT id FROM Sensors WHERE name = Temperature), 'FALSE', 'pv * 9 / 5 + 32'),
	        ('Kelvin',              'K',    2, (SELECT id FROM Sensors WHERE name = Temperature), 'FALSE', 'pv + 273.15'),
	        ('Grama',               'g',    3, (SELECT id FROM Sensors WHERE name = Mass), 'FALSE', 'pv * 1000'),
	        ('Kilo',                'kg',   3, (SELECT id FROM Sensors WHERE name = Mass), 'TRUE', 'pv'),
	        ('Tonelada',            't',    2, (SELECT id FROM Sensors WHERE name = Mass), 'FALSE', 'pv / 1000'),
	        ('Segundo',             's',    3, (SELECT id FROM Sensors WHERE name = Time), 'TRUE', 'pv'),
	        ('Minuto',              'min',  2, (SELECT id FROM Sensors WHERE name = Time), 'FALSE', 'pv / 60'),
	        ('Hora',                'h',    2, (SELECT id FROM Sensors WHERE name = Time), 'FALSE', 'pv / 120'),
	        ('Ampere',              'A',    2, (SELECT id FROM Sensors WHERE name = CurrentEletric), 'TRUE', 'pv'),
	        ('Volts',               'V',    2, (SELECT id FROM Sensors WHERE name = EletricTension), 'TRUE', 'pv'),
	        ('Lumens',              'lm',   2, (SELECT id FROM Sensors WHERE name = LightIntensity), 'TRUE', 'pv'),
	        ('Bar',                 'bar',  3, (SELECT id FROM Sensors WHERE name = Pressure), 'FALSE', 'pv / 100000'),
	        ('Pascal',              'Pa',   2, (SELECT id FROM Sensors WHERE name = Pressure), 'TRUE', 'pv'),
	        ('Newton',              'N',    2, (SELECT id FROM Sensors WHERE name = Force), 'TRUE', 'pv'),
	        ('Kilograma força',     'Kgf',  3, (SELECT id FROM Sensors WHERE name = Force), 'FALSE', 'pv * 0.101972'),
            ('Watt',                'W',    2, (SELECT id FROM Sensors WHERE name = Power), 'TRUE', 'pv'),
	        ('Miliwatt',            'mW',   3, (SELECT id FROM Sensors WHERE name = Power), 'FALSE', 'pv * 1000'),
		    ('Decibeis',            'dB',   0, (SELECT id FROM Sensors WHERE name = Sound), 'TRUE', 'pv'),
            ('Aberto/Fechado',      NULL,   NULL, (SELECT id FROM Sensors WHERE name = State), 'TRUE', NULL),
            ('Ligado/Desligado',    NULL,   NULL, (SELECT id FROM Sensors WHERE name = State), 'FALSE', NULL),
            ('Texto',               NULL,   NULL, (SELECT id FROM Sensors WHERE name = Message), 'TRUE', NULL),
            ('Imagem',              NULL,   NULL, (SELECT id FROM Sensors WHERE name = Message), 'FALSE', NULL),
            ('Umidade Relativa',     '%',   2, (SELECT id FROM Sensors WHERE name = Humidity), 'TRUE', 'pv');
            
END;
$$ LANGUAGE plpgsql;

