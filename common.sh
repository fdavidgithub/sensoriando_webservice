#
# Set 1 to verbose mode: on
# Set 0 to verbose mode: off
#
export VERBOSE=1

# 
# Local directory
#
if [ -z $HOST ]; then
    export HOST=$(pwd)
fi

# 
# Log file
#
export LOG=$HOST/sensoriando.log

# 
# Functions
#
log() {
    if [ $VERBOSE == 1 ]; then
        echo $1
    fi

    DT=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$DT|$1" >> $LOG
}

db_log() {
    if [ $VERBOSE == 1 ]; then
        echo $1
    fi

    SQL="INSERT INTO Log (message) VALUES ('$1')" 
    psql -c "$SQL"
}

# 
# Check config file
#
export CONFIG=$HOST/sensoriando.conf

if [ -e $CONFIG ]; then
    log "Config file in use: $CONFIG"
else    
    log "Config file not found"
    exit 0
fi

# 
# PostgreSQL: Environments variables
# https://www.postgresql.org/docs/current/libpq-envars.html
#
export PGDATABASE=$(awk -F "=" '/db_name/ {print $2}' $CONFIG)
export PGHOST=$(awk -F "=" '/db_host/ {print $2}' $CONFIG)
export PGPORT=$(awk -F "=" '/db_port/ {print $2}' $CONFIG)
export PGUSER=$(awk -F "=" '/db_user/ {print $2}' $CONFIG)
export PGPASSWORD=$(awk -F "=" '/db_passwd/ {print $2}' $CONFIG)

log "Database: $PGDATABASE | Host: $PGHOST | Port: $PGPORT | Username: $PGUSER | Password: $PGPASSWORD"


