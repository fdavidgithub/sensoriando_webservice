CREATE OR REPLACE VIEW vwThingsData AS
    SELECT  ID.id, 
            ID.dt, 
            ID.id_thing,
            ID.qos,
            ID.retained,
            TO_TIMESTAMP(REPLACE(CAST(ID.payload->>'dt' AS TEXT), '"', ''), 'YYYYMMDDHH24MISS') payload_dt, 
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
    
    
