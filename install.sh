# Create database and set config files
#!/bin/bash
source common.sh
SQL=$HOST/db

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
#    createdb -U $DB_USER $DB_NAME
    createdb
    log "$MSG"

    MSG="Creating tables from $TABLES"
    if [ -e $TABLES ]; then
#        psql -U $DB_USER -d $DB_NAME -f $TABLES
        psql -f $TABLES
 
	MSG="${MSG} OK"
    else
        MSG="${MSG} FAIL"
    fi   
    log "$MSG"

    MSG="Creating views from $VIEWS"
    if [ -e $VIEWS ]; then
#        psql -U $DB_USER -d $DB_NAME -f $VIEWS
        psql -f $VIEWS

	MSG="${MSG} OK"
    else
        MSG="${MSG} FAIL"
    fi   
    log "$MSG"

    MSG="Insert records from $INSERTS:"
    if [ -e $INSERTS ]; then
#        psql -U $DB_USER -d $DB_NAME -f $INSERTS
        psql -f $INSERTS
 
	MSG="${MSG} OK"
    else
        MSG="${MSG} FAIL"
    fi   
    log "$MSG"

    MSG="Creating functions from $FUNCTIONS"
    if [ -e $FUNCTIONS ]; then
#        psql -U $DB_USER -d $DB_NAME -f $FUNCTIONS
        psql -f $FUNCTIONS
 
	MSG="${MSG} OK"
    else
        MSG="${MSG} FAIL"
    fi   
    log "$MSG"

    MSG="Creating triggers from $TRIGGERS"
    if [ -e $TRIGGERS ]; then
#        psql -U $DB_USER -d $DB_NAME -f $TRIGGERS
        psql -f $TRIGGERS
 
	MSG="${MSG} OK"
    else
        MSG="${MSG} FAIL"
    fi   
    log "$MSG"
}

# 
# Main script
#
setdatabase

exit 0

