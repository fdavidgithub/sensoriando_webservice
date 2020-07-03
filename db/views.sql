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

CREATE OR REPLACE VIEW vwAccountsThingsModulesSensorsUnits AS
    SELECT  ROW_NUMBER() OVER() AS id, /* need to Django ORM */
            A.id_account,
            A.id_thing,
            A.id_module,
            A.id_modulesensor,
            A.id_sensor,
            A.id_sensorunit
    FROM (    
    
    SELECT DISTINCT
        A.id AS id_account,
        T.id AS id_thing,
        MS.id_module AS id_module,
        MS.id AS id_modulesensor,
        SU.id_sensor AS id_sensor,
        SU.id AS id_sensorunit
    FROM Accounts A
        INNER JOIN AccountsThings AT ON AT.id_account = A.id
        INNER JOIN Things T ON T.id = AT.id_thing
        INNER JOIN ThingsModulesSensorsData TD ON TD.id_thing = T.id
        INNER JOIN ModulesSensors MS ON MS.id = TD.id_modulesensor
        INNER JOIN SensorsUnits SU ON SU.id_sensor = MS.id_sensor
                                  AND SU.isdefault = 'TRUE'
    WHERE A.status = 'TRUE'
    
    ) A;

