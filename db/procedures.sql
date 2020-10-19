CREATE OR REPLACE PROCEDURE DatumFromJson(id_payload INTEGER) AS
$$
BEGIN
    INSERT INTO ThingsModulesSensorsData (id_payload, /*id_thing,*/ id_thingsensor, dtread, value, message)
    SELECT  p.id,
/*
            (SELECT t.id
             FROM Things t
             WHERE t.uuid = SUBSTRING(p.topic, 1, STRPOS(p.topic, '/')-1)::UUID),
*/            
            SUBSTRING(p.topic, STRPOS(c.topic, '/')+1, LENGTH(c.topic))::INTEGER, 

            CASE 
                WHEN p.payload->>'dt' IS NOT NULL 
                    THEN TIMEZONE('UTC', CAST(TO_TIMESTAMP(p.payload->>'dt', 'YYYYMMDDHH24MISS') AS VARCHAR)::TIMESTAMP)
                ELSE p.dt
            END,

            CASE 
                WHEN p.payload->>'value'::varchar ~ '^[0-9\.]+$' = True
                    THEN CAST(p.payload->>'value' AS FLOAT)
                ELSE NULL
            END,
 
            CASE 
                WHEN p.payload->>'value'::varchar ~ '^[0-9\.]+$' = False
                    THEN CAST(p.payload->>'value' AS VARCHAR)
                ELSE NULL
            END
    FROM Payloads p
      INNER JOIN Connections c ON c.id = p.id_connection
    WHERE p.id = id_payload;
      
END;
$$ LANGUAGE plpgsql;

