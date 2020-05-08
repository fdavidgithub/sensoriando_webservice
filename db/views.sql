CREATE OR REPLACE VIEW vwThingsData AS
    SELECT  ID.id, 
            ID.dt, 
            ID.id_thing,
            ID.id_sensor,
            ID.qos,
            ID.retained,

            CASE WHEN ID.payload->>'dt' IS NOT NULL 
                THEN TO_TIMESTAMP(REPLACE(CAST(ID.payload->>'dt' AS TEXT), '"', ''), 'YYYYMMDDHH24MISS')
                ELSE ID.dt
            END payload_dt,

            CAST(ID.payload->>'value' AS REAL) payload_value
    FROM ThingsData ID;


CREATE OR REPLACE VIEW vwAccountsThings AS
    SELECT A.id AS id_account,
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
    SELECT DISTINCT
        A.id AS id_account,
        T.id AS id_thing,
        S.id AS id_sensor,
        SU.id AS id_unit
    FROM Accounts A
        INNER JOIN AccountsThings AT ON AT.id_account = A.id
        INNER JOIN Things T ON T.id = AT.id_thing
        INNER JOIN ThingsData TD ON TD.id_thing = T.id
        INNER JOIN Sensors S ON S.id = TD.id_sensor
        INNER JOIN SensorsUnits SU ON SU.id_sensor = S.id
                                  AND SU.isdefault = 'TRUE'
    WHERE A.status = 'TRUE'
    ORDER BY A.id, T.id, S.id;

