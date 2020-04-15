#Sensoriando
**Setup**

## Mosquitto
```console
sudo systemctl stop mosquitto

export CFG_DIR=/etc/mosquitto
export CFG_FILE=$CFG_DIR/mosquitto.conf
export PWD_FILE=sensoriando.pwd
```

1. Set security mode
```console
sudo echo "" >> $CFG_FILE
sudo echo "# =================================================" >> $CFG_FILE
sudo echo "# Sensoriando: Settings" >> $CFG_FILE
sudo echo "# =================================================" >> $CFG_FILE
sudo echo "allow_anonymous false" >> $CFG_FILE
sudo echo "password_file $CFG_DIR/$PWD_FILE" >> $CFG_FILE
```

2. Create user
```console
export MQTT_USER=fdavid
sudo mosquitto_passwd -c $CFG_DIR/$PWD_FILE $MQTT_USER
```

3. Test
```console
export MQTT_PASSWD=12345678 
sudo systemctl start mosquitto

mosquitto_sub -h localhost -t test -u $MQTT_USER -P $MQTT_PASSWD
mosquitto_pub -h localhost -t test -m 'hello broker' -u $MQTT_USER -P $MQTT_PASSWD
```

## Django
```console

```
