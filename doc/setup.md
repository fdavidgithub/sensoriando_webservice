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
sudo echo "Sensoriando: Settings" >> $CFG_FILE
sudo echo "allow_anonymous false" >> $CFG_FILE
sudo echo "password_file $CFG_DIR/$PWD_FILE" >> $CFG_FILE
```

2. Create user
```console
export USER=fdavid

sudo mosquitto_passwd -c $CFG_DIR/$PWD_FILE $USER
```

3. Test
```console
export PWD=12345678 
sudo system_ctl start mosquitto

mosquitto_sub -h localhost -t test -u $USER -P $PWD
mosquitto_pub -h localhost -t test -m 'hello broker' -u $USER -P $PWD
```
