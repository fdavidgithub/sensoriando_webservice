# Create database and set config files
#!/bin/bash
source common.sh
SQL=$HOST/db

#
# Functions
#
setdatabase() {
    CREATE=$SQL/create.sql
    TABLES=$SQL/tables.sql
    FUNCTIONS=$SQL/functions.sql
    PROCEDURES=$SQL/procedures.sql
    TRIGGERS=$SQL/triggers.sql
    INSERTS=$SQL/inserts.sql
    VIEWS=$SQL/views.sql

    MSG="Create database... "
    createdb $DB_NAME
    psql -f $CREATE
    log "$MSG"


    MSG="Creating tables from $TABLES"
    if [ -e $TABLES ]; then
        psql -f $TABLES
 
	MSG="${MSG} OK"
    else
        MSG="${MSG} FAIL"
    fi   
    log "$MSG"


    MSG="Creating views from $VIEWS"
    if [ -e $VIEWS ]; then
        psql -f $VIEWS

	MSG="${MSG} OK"
    else
        MSG="${MSG} FAIL"
    fi   
    log "$MSG"


    MSG="Insert records from $INSERTS:"
    if [ -e $INSERTS ]; then
        psql -f $INSERTS
 
	MSG="${MSG} OK"
    else
        MSG="${MSG} FAIL"
    fi   
    log "$MSG"


    MSG="Creating procedures from $PROCEDURES"
    if [ -e $PRODECURES ]; then
        psql -f $PROCEDURES
 
	MSG="${MSG} OK"
    else
        MSG="${MSG} FAIL"
    fi   
    log "$MSG"


    MSG="Creating functions from $FUNCTIONS"
    if [ -e $FUNCTIONS ]; then
        psql -f $FUNCTIONS
 
	MSG="${MSG} OK"
    else
        MSG="${MSG} FAIL"
    fi   
    log "$MSG"


    MSG="Creating triggers from $TRIGGERS"
    if [ -e $TRIGGERS ]; then
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

