# Create a Payload for test
#!/bin/bash
source common.sh

UUID=$(psql -c "select uuid from things where id = 1" -t)
SENSOR=$(psql -c "select id from sensors where id = 1" -t)
QOS=1		# 0, 1 or 2
RETAINED=1 	# 1 true or 0 false

VALUE=$(((RANDOM % 100) +1))
DATE=$(date '+%Y%m%d%H%M%S')

PAYLOAD="{\"dt\": \"$DATE\", \"value\": $VALUE}"
USER=fdavid
PASSWD=12345678

TOPIC=$UUID/$SENSOR
TOPIC=$(echo $TOPIC | sed 's/ //g') #Remove whitespace

echo "Thing  : $UUID"
echo "Sensor : $SENSOR"
echo "Topic  : $TOPIC"
echo "Payload: $PAYLOAD"

if [ $RETAINED == 1 ]; then
	mosquitto_pub -h localhost -r -q $QOS -t $TOPIC -m "$PAYLOAD" -u $USER -P $PASSWD
else
	mosquitto_pub -h localhost -q $QOS -t $TOPIC -m "$PAYLOAD" -u $USER -P $PASSWD
fi

