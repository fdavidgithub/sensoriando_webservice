CREATE OR REPLACE VIEW vwAccountsThings AS
    SELECT ROW_NUMBER() OVER() AS id, /* need to Django ORM */
           A.id AS id_account,
           A.dt AS dt_account,
           A.city,
           A.state,
           A.country,
           A.usetrigger,
           A.ispublic,
           T.id AS id_thing,
           T.dt AS dt_thing,
           T.name AS thing,
           T.uuid,
           T.isrelay
    FROM Accounts A
        INNER JOIN AccountsThings AT ON AT.id_account = A.id
        INNER JOIN Things T ON T.id = AT.id_thing
    WHERE A.status = 'TRUE';

CREATE OR REPLACE VIEW vwAccountsThingsSensorsUnits AS
    SELECT  ROW_NUMBER() OVER() AS id, /* need to Django ORM */
            A.id_account,
            A.id_thing,
            A.id_sensor,
            A.id_unit
    FROM (    
    
    SELECT DISTINCT
        A.id AS id_account,
        T.id AS id_thing,
        S.id AS id_sensor,
        SU.id AS id_unit
    FROM Accounts A
        INNER JOIN AccountsThings AT ON AT.id_account = A.id
        INNER JOIN Things T ON T.id = AT.id_thing
        INNER JOIN ThingsSensorsData TD ON TD.id_thing = T.id
        INNER JOIN Sensors S ON S.id = TD.id_sensor
        LEFT JOIN SensorsUnits SU ON SU.id_sensor = S.id
                                 AND SU.isdefault = 'TRUE'
    WHERE A.status = 'TRUE'
    ORDER BY A.id, T.id, S.id
    
    ) A;

