CREATE OR REPLACE VIEW vwThingsData AS
    SELECT  ROW_NUMBER() OVER() AS id, /* need to Django ORM */  
            TD.id AS id_thingdatum, 
            TD.dt AS dt_thingdatum, 
            TD.id_thing,
            TD.id_sensor,
            TD.qos,
            TD.retained,

            CASE 
                WHEN TD.payload->>'dt' IS NOT NULL 
                    THEN TIMEZONE('UTC', CAST(TO_TIMESTAMP(TD.payload->>'dt', 'YYYYMMDDHH24MISS') AS VARCHAR)::TIMESTAMP)
                ELSE TD.dt
            END AS payload_dt,

            CASE 
                WHEN (TD.payload->>'value' IS NOT NULL) AND (TD.payload->>'value'::varchar ~ '^[0-9\.]+$' = True)
                    THEN CAST(TD.payload->>'value' AS FLOAT)
                WHEN (TD.payload->>'value' IS NULL) AND (TD.payload::varchar ~ '^[0-9\.]+$' = True)
                    THEN CAST(CAST(TD.payload AS TEXT) AS FLOAT)
                ELSE NULL
            END AS payload_value,

            CASE 
                WHEN (TD.payload->>'value' IS NOT NULL) AND (TD.payload->>'value'::varchar ~ '^[0-9\.]+$' = False)
                    THEN CAST(TD.payload->>'value' AS TEXT)
                WHEN (TD.payload->>'value' IS NULL) AND (TD.payload->>'dt' IS NULL) AND (TD.payload::varchar ~ '^[0-9\.]+$' = False)
                    THEN CAST(TD.payload AS TEXT)
                ELSE NULL
            END AS payload_message
    FROM ThingsData TD
    ORDER BY TD.id;

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
        INNER JOIN ThingsData TD ON TD.id_thing = T.id
        INNER JOIN Sensors S ON S.id = TD.id_sensor
        LEFT JOIN SensorsUnits SU ON SU.id_sensor = S.id
                                 AND SU.isdefault = 'TRUE'
    WHERE A.status = 'TRUE'
    ORDER BY A.id, T.id, S.id
    
    ) A;

