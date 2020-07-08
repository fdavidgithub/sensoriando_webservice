DO $$
DECLARE 
    /*
     * Sensors
     */
    Volume          VARCHAR := 'Volume';
    Distance        VARCHAR := 'Distancia';
    Temperature     VARCHAR := 'Temperatura';
    Mass            VARCHAR := 'Massa';
    RTC             VARCHAR := 'TempoRTC';
    CurrentEletric  VARCHAR := 'Corrente Eletrica';
    EletricTension  VARCHAR := 'Tensao Eletrica';
    LightIntensity  VARCHAR := 'Intensidade Luminosa';
    Pressure        VARCHAR := 'Pressao';
    Force           VARCHAR := 'Forca';
    Power           VARCHAR := 'Potencia';
    Sound           VARCHAR := 'Som';
    State           VARCHAR := 'Estado';
    Message         VARCHAR := 'Mensagem';
    Humidity        VARCHAR := 'Umidade';
    Storage         VARCHAR := 'Armazenamento';

    /* 
     * Modules
     */
    System          VARCHAR := 'Sistema';
    Loud            VARCHAR := 'Sonoro';
    Weather         VARCHAR := 'Clima';
BEGIN
    INSERT INTO Plans  (name) VALUES ('Gratuito');
    INSERT INTO Things (name) VALUES ('Prototypes');
    
    INSERT INTO Sensors (name)
    VALUES	(RTC),
            (Storage),
            (Message),
            (Volume),
	        (Distance),
	        (Temperature),
	        (Mass),
	        (CurrentEletric),
	        (EletricTension),
	        (LightIntensity),
	        (Pressure),
	        (Force),
            (Power),
            (Sound),
            (State),
            (Humidity);

    INSERT INTO SensorsUnits (name, initial, precision, id_sensor, isdefault, expression)
    VALUES	('Litro',               'l',    3, (SELECT id FROM Sensors WHERE name = Volume), 'FALSE', 'pv * 1000'),
            ('Centimetro Cubico',   'cm^3', 3, (SELECT id FROM Sensors WHERE name = Volume), 'FALSE', 'pv * 1000000'),
    	    ('Metro Cubico',        'm^3',  3, (SELECT id FROM Sensors WHERE name = Volume), 'TRUE',  'pv'),

	        ('Milimitro',           'mm',   2, (SELECT id FROM Sensors WHERE name = Distance), 'FALSE', 'pv * 1000'),
	        ('Centimetro',          'cm',   2, (SELECT id FROM Sensors WHERE name = Distance), 'FALSE', 'pv * 100'),
	        ('Metro',               'm',    2, (SELECT id FROM Sensors WHERE name = Distance), 'TRUE',  'pv'),
	        ('Kilometro',           'km',   2, (SELECT id FROM Sensors WHERE name = Distance), 'FALSE', 'pv / 1000'),

	        ('Celsio',              'C',    2, (SELECT id FROM Sensors WHERE name = Temperature), 'FALSE', 'pv - 273.15'),
	        ('Farenhit',            'F',    2, (SELECT id FROM Sensors WHERE name = Temperature), 'FALSE', '(pv - 273.15) * 9 / 5 + 32'),
	        ('Kelvin',              'K',    2, (SELECT id FROM Sensors WHERE name = Temperature), 'TRUE',  'pv'),

	        ('Grama',               'g',    3, (SELECT id FROM Sensors WHERE name = Mass), 'FALSE', 'pv * 1000'),
	        ('Kilo',                'kg',   3, (SELECT id FROM Sensors WHERE name = Mass), 'TRUE',  'pv'),
	        ('Tonelada',            't',    2, (SELECT id FROM Sensors WHERE name = Mass), 'FALSE', 'pv / 1000'),

	        ('Segundo',             's',    3, (SELECT id FROM Sensors WHERE name = RTC), 'TRUE',  'pv'),
	        ('Minuto',              'min',  2, (SELECT id FROM Sensors WHERE name = RTC), 'FALSE', 'pv / 60'),
	        ('Hora',                'h',    2, (SELECT id FROM Sensors WHERE name = RTC), 'FALSE', 'pv / 120'),

	        ('Ampere',              'A',    2, (SELECT id FROM Sensors WHERE name = CurrentEletric), 'TRUE', 'pv'),

	        ('Volts',               'V',    2, (SELECT id FROM Sensors WHERE name = EletricTension), 'TRUE', 'pv'),

	        ('Candela',             'cd',   2, (SELECT id FROM Sensors WHERE name = LightIntensity), 'TRUE', 'pv'),

	        ('Bar',                 'bar',  3, (SELECT id FROM Sensors WHERE name = Pressure), 'FALSE', 'pv / 100000'),
	        ('Psi',                 'psi',  3, (SELECT id FROM Sensors WHERE name = Pressure), 'FALSE', 'pv * 0.0001450377'),
            ('Pascal',              'Pa',   2, (SELECT id FROM Sensors WHERE name = Pressure), 'TRUE',  'pv'),

	        ('Newton',              'N',    2, (SELECT id FROM Sensors WHERE name = Force), 'TRUE',  'pv'),
	        ('Kilograma forca',     'Kgf',  3, (SELECT id FROM Sensors WHERE name = Force), 'FALSE', 'pv * 0.101972'),

            ('Watt',                'W',    2, (SELECT id FROM Sensors WHERE name = Power), 'TRUE',  'pv'),
	        ('Miliwatt',            'mW',   3, (SELECT id FROM Sensors WHERE name = Power), 'FALSE', 'pv * 1000'),

		    ('Decibeis',            'dB',   0, (SELECT id FROM Sensors WHERE name = Sound), 'TRUE', 'pv'),

            ('Aberto/Fechado',      NULL,   NULL, (SELECT id FROM Sensors WHERE name = State), 'TRUE', NULL),
            ('Ligado/Desligado',    NULL,   NULL, (SELECT id FROM Sensors WHERE name = State), 'FALSE', NULL),

            ('Texto',               NULL,   NULL, (SELECT id FROM Sensors WHERE name = Message), 'TRUE', NULL),
            ('Imagem',              NULL,   NULL, (SELECT id FROM Sensors WHERE name = Message), 'FALSE', NULL),

            ('Umidade Relativa',     '%',   2, (SELECT id FROM Sensors WHERE name = Humidity), 'TRUE', 'pv'),

            ('Byte',                 'B',   2, (SELECT id FROM Sensors WHERE name = Storage), 'FALSE', 'pv * 1024'),
            ('Kilobyte',            'KB',   2, (SELECT id FROM Sensors WHERE name = Storage), 'TRUE', 'pv'),
            ('Megabyte',            'MB',   2, (SELECT id FROM Sensors WHERE name = Storage), 'FALSE', 'pv / 1024'),
            ('Gigabyte',            'GB',   2, (SELECT id FROM Sensors WHERE name = Storage), 'FALSE', '(pv / 1024) / 1024');


    INSERT INTO Modules (name)
    VALUES	(System),
            (Loud),
            (Weather);
 
    INSERT INTO ModulesSensors (id_module, id_sensor)
    VALUES ((SELECT id FROM Modules WHERE name = System), (SELECT id FROM Sensors WHERE name = RTC)),
           ((SELECT id FROM Modules WHERE name = System), (SELECT id FROM Sensors WHERE name = Storage)),
           ((SELECT id FROM Modules WHERE name = System), (SELECT id FROM Sensors WHERE name = Message)),
        
           ((SELECT id FROM Modules WHERE name = Loud), (SELECT id FROM Sensors WHERE name = Sound)),

           ((SELECT id FROM Modules WHERE name = Weather), (SELECT id FROM Sensors WHERE name = Temperature)),
           ((SELECT id FROM Modules WHERE name = Weather), (SELECT id FROM Sensors WHERE name = Humidity));

END;
$$ LANGUAGE plpgsql;

