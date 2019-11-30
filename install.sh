# Create database and set config files
#!/bin/bash

#
# Set 1 to verbose mode: on
# Set 0 to verbose mode: off
#
VERBOSE=1

# 
# Functions
#
logging() {
    if [ $VERBOSE == 1 ]; then
        echo $1
    fi

    DT=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$DT|$1" >> $LOG 
}

#
# Setting
#
if [ -z $HOST ]; then
    HOST=/mnt/data/git/Sensoriando
fi

DB_HOST=localhost
DB_NAME=sensoriando
DB_USER=postgres
LOG=$HOST/sensoriando.log
SQL=./db

# Cheking system
if [ ! -e $LOG ]; then
    touch $LOG
fi

#
# Functions
#
setdatabase() {
    TABLES=$SQL/tables.sql
    FUNCTIONS=$SQL/functions.sql
    TRIGGERS=$SQL/triggers.sql
    INSERTS=$SQL/inserts.sql
    VIEWS=$SQL/views.sql

    MSG="Create database... "
    createdb -U $DB_USER $DB_NAME
    logging "$MSG"

    MSG="Creating tables:"
    if [ -e $TABLES ]; then
        psql -U $DB_USER -d $DB_NAME -f $TABLES
        MSG="${MSG} OK"
    else
        MSG="${MSG} FAIL"
    fi   
    logging "$MSG"

    MSG="Creating views:"
    if [ -e $VIEWS ]; then
        psql -U $DB_USER -d $DB_NAME -f $VIEWS
        MSG="${MSG} OK"
    else
        MSG="${MSG} FAIL"
    fi   
    logging "$MSG"

    MSG="Insert records:"
    if [ -e $INSERTS ]; then
        psql -U $DB_USER -d $DB_NAME -f $INSERTS
        MSG="${MSG} OK"
    else
        MSG="${MSG} FAIL"
    fi   
    logging "$MSG"

    MSG="Creating functions:"
    if [ -e $FUNCTIONS ]; then
        psql -U $DB_USER -d $DB_NAME -f $FUNCTIONS
        MSG="${MSG} OK"
    else
        MSG="${MSG} FAIL"
    fi   
    logging "$MSG"

    MSG="Creating triggers:"
    if [ -e $TRIGGERS ]; then
        psql -U $DB_USER -d $DB_NAME -f $TRIGGERS
        MSG="${MSG} OK"
    else
        MSG="${MSG} FAIL"
    fi   
    logging "$MSG"
}


# 
# Main script
#
setdatabase

exit 0

