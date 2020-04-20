CREATE OR REPLACE VIEW vwThingsData AS
    SELECT  ID.id, 
            ID.dt, 
            ID.id_thing,
            ID.qos,
            ID.retained,
            TO_TIMESTAMP(REPLACE(CAST(ID.payload->>'dt' AS TEXT), '"', ''), 'YYYYMMDDHH24MISS') payload_dt, 
            CAST(ID.payload->>'value' AS REAL) payload_value,
            CAST(ID.payload->>'sensor' AS INTEGER) payload_sensor             
    FROM ThingsData ID;

