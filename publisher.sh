# Create a Payload for test
#!/bin/bash
source common.sh

TOPIC_TEST=$(psql -c "select token from things where id = 1" -t)
SENSOR_TEST=$(psql -c "select id from sensors where id = 1" -t)
QOS_TEST=1		# 0, 1 or 2
RETAINED_TEST=1 	# 1 true or 0 false

VALUE=$(((RANDOM % 100) +1))
DATE=$(date '+%Y%m%d%H%M%S')

PAYLOAD="{\"dt\": \"$DATE\", \"sensor\": $SENSOR_TEST, \"value\": $VALUE}"
USER=fdavid
PASSWD=12345678

echo "Topic: $TOPIC_TEST"
echo "Sensor: $SENSOR_TEST"
echo "Payload: $PAYLOAD"

if [ $RETAINED_TEST == 1 ]; then
	mosquitto_pub -h localhost -r -q $QOS_TEST -t $TOPIC_TEST -m "$PAYLOAD" -u $USER -P $PASSWD
else
	mosquitto_pub -h localhost -q $QOS_TEST -t $TOPIC_TEST -m "$PAYLOAD" -u $USER -P $PASSWD
fi

