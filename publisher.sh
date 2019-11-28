#!/bin/bash

TOPIC_TEST=$(psql -U postgres -d sensoriando -c "select token from iots where id = 1" -t)

SENSOR_TEST=$(psql -U postgres -d sensoriando -c "select id from iotssensors where id = 1" -t)

USER=fdavid
PASSWD=12345678

VALUE=$(((RANDOM % 100) +1))
DATE='20191105211425'

PAYLOAD="{\"dt\": \"$DATE\", \"sensor\": $SENSOR_TEST, \"value\": $VALUE}"

mosquitto_pub -h localhost -t $TOPIC_TEST -m "$PAYLOAD" -u $USER -P $PASSWD

