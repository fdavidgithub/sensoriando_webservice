# Sensoriando
**Requirement**

Homologated
* Ubuntu 18.04

```console
sudo apt-get update
sudo apt-get upgrade
```

### Database
```console
sudo apt-get postgresql
sudo vi /etc/postgres/10/main/pg_hda.conf
```

after: local	all	postgres	peer
before: local	all	postgres	trust

```console
sudo systemctl restart postgresql
```

### Framework
```console
sudo apt-get install python3-pip
pip install django psycopg2 psycopg2-binary
sudo apt-get install python-psycopg2
```

### Broker MQTT
```console
sudo apt-get install mosquitto mosquitto-clients
```

### NTP
```console
sudo apt-get install ntp
sudo timedatectl set-timezone America/Sao_Paulo
sudo apt-get install ntpdate
service ntp stop
sudo service ntp stop
sudo ntpdate a.ntp.br
sudo service ntp start
```

### Development
```console
sudo apt-get install build-essential gcc make cmake cmake-gui cmake-curses-gui
sudo apt-get install libssl-dev 
sudo apt-get install doxygen

git clone https://github.com/eclipse/paho.mqtt.c.git
cd paho.mqtt.c
make
make html
sudo make install
```

