#!/bin/bash
source common.sh
source errors.sh

export SENSORIANDO_WEBDIR=$(pwd)
export ENV_DIR="$SENSORIANDO_WEBDIR/venv"
export PROFILE="/etc/profile"
export ENVIRONMENT="export SENSORIANDO_WEBDIR=$SENSORIANDO_WEBDIR"
export SETTINGS_DIR="/etc/sensoriando"
export SETTINGS_FILE="$SETTINGS_DIR/settings.conf"
export SYSTEMD="/usr/lib/systemd/system"

log "[INSTALL]"


## CHECKING DEPENDENCES
which python3
if [ $? ]; then
    log "[ERROR] Python3 not installed"
    exit $PYTHON_NOTFOUND
fi      

which psql
if [ $? ]; then
    log "[ERROR] PostgreSQL not installed"
    exit $POSTGRE_NOTFOUND
fi      

DB=$(psql -U postgres -l | grep sensoriando)
if [ -z $DB ]; then
    log "[ERROR] Database not exist"
    exit $DATABASE_NOTFOUND
fi


## SETTINGS
log "[INFO] Settings files..."

# Create directory if not exists
sudo mkdir -p $SETTINGS_DIR

# Create minimal settings if not exist file
if [ ! -e $SETTINGS_FILE ]; then
    sudo cp $SENSORIANDO_WEBDIR/confs/settings.conf $SETTINGS_FILE
fi


## VARIABLE ENVIRONMENT
log "[INFO] Variable environment..."

# Check profile file exists
if [ -f $PROFILE ]; then
    #Append line if not exists
    if [ -z "$(cat $PROFILE | grep "$ENVIRONMENT")" ]; then
        echo "$ENVIRONMENT" | sudo tee -a $PROFILE
    fi
else
    log "[ERROR] $PROFILE do not exists, check install"
    exit $INSTALL_PROFILE
fi


## DAEMON
log "[INFO] Daemon..."

# Check if systemd installed
if [ -d $SYSTEMD ]; then
    log "[ERROR] $SYSTEMD not found, check install"
    exit $INSTALL_SYSTEMD
fi

sudo cp $SENSORIANDO_WEBDIR/confs/sensoriando_web.service $SYSTEMD/sensoriando_web.service

#Search and replace tag SENSORIANDO_WEBDIR by variable enviroment
sudo sed -i "s|@SENSORIANDO_WEBDIR|$SENSORIANDO_WEBDIR|g" $SYSTEMD/sensoriando_web.service

sudo systemctl enable sensoriando_web
sudo systemctl start sensoriando_web


## REQUIREMENTS
log "[INFO] Requirements..."

# Check if not exists directory 
if [ ! -d "$ENV_DIR" ]; then
    python3 -m venv venv
fi

source $SENSORIANDO_WEBDIR/venv/bin/activate
pip3 install -r $SENSORIANDO_WEBDIR/requirements.txt > /dev/null


## Django settings
log "[INFO] Django..."

python $SENSORIANDO_WEBDIR/manage.py makemigrations
python $SENSORIANDO_WEBDIR/manage.py migrate
python $SENSORIANDO_WEBDIR/manage.py createsuperuser


## Done
log "[INFO] Success instalation."
echo "Restart system"
exit $SUCCESS

