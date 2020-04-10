# Create a Payload for test
#!/bin/bash
source common.sh

TOPIC_TEST=$(psql -c "select token from things where id = 1" -t)
SENSOR_TEST=$(psql -c "select id from thingssensors where id = 1" -t)

echo "Topic: $TOPIC_TEST"
echo "Sensor: $SENSOR_TEST"

VALUE=$(((RANDOM % 100) +1))
DATE=$(date '+%Y%m%d%H%M%S')

PAYLOAD="{\"dt\": \"$DATE\", \"sensor\": $SENSOR_TEST, \"value\": $VALUE}"
USER=fdavid
PASSWD=12345678

mosquitto_pub -h localhost -t $TOPIC_TEST -m "$PAYLOAD" -u $USER -P $PASSWD

