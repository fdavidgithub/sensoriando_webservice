#include <stdio.h>
#include <stdlib.h>

#include "database.h"

/* 
 * Functions
 */
void do_exit(PGconn *conn) 
{
    PQfinish(conn);
}
 
PGconn* do_connect(char *db, char *user, char *passwd, char *host)
{
    char string_connect[256];

    sprintf(string_connect, "password=%s user=%s dbname=%s host=%s", passwd, user, db, host);
    PGconn *conn = PQconnectdb(string_connect);
   
    if (PQstatus(conn) == CONNECTION_BAD) {
        fprintf(stderr, "Connection to database failed: %s\n", PQerrorMessage(conn));
        do_exit(conn);
    }

#ifdef DEBUG
    printf("User: %s\n", PQuser(conn));
    printf("Database name: %s\n", PQdb(conn));
    printf("Password: %s\n", PQpass(conn));
#endif
    
    return conn;
}

int
payload_insert(PGconn *conn, Payload *payload)
{
    PGresult *res;
    char sql[256];

    sprintf(sql, "INSERT INTO Payloads (payload, qos, retained, topic) \
                  VALUES ('%s', %d, '%d', '%s')", \
                  payload->payload, payload->qos, payload->retained, payload->topic);

#ifdef DEBUG
    printf("%s\n", sql);
#endif

    res = PQexec(conn, sql);
    PQclear(res);    
 
    return PQresultStatus(res) == PGRES_COMMAND_OK; 
}


Thing *
get_thing_uuid(PGconn *conn, char *topic)
{
    PGresult *res;
    Thing *thing = NULL;
    char sql[256];
    int rows;

    sprintf(sql, "SELECT id, dt, name, uuid \
                  FROM Things \
                  WHERE uuid = '%s'", topic);

#ifdef DEBUG
    printf("%s\n", sql);
#endif

    res = PQexec(conn, sql);    
    rows = PQntuples(res);

    if ( (PQresultStatus(res) == PGRES_TUPLES_OK) && rows ) {
        thing = malloc(sizeof *thing);

        if ( thing != NULL ) {
            thing->id = atoi(PQgetvalue(res, 0, 0));
            sprintf(thing->dt, "%s", PQgetvalue(res, 0, 1));
            sprintf(thing->name, "%s", PQgetvalue(res, 0, 2));
            sprintf(thing->uuid, "%s", PQgetvalue(res, 0, 3));
        } else {
            printf("Error malloc\n");
        }
    } else {
        printf("No data retrieved\n");        
    } 

    PQclear(res);
    return thing;
}

