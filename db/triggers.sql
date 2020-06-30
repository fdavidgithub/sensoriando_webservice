DROP TRIGGER IF EXISTS aiPayloads ON Payloads;
CREATE TRIGGER aiPayloads AFTER INSERT ON Payloads
FOR EACH ROW
    EXECUTE PROCEDURE ThingsSensorsDataCreate();
    
