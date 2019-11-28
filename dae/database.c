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
/*
    printf("User: %s\n", PQuser(conn));
    printf("Database name: %s\n", PQdb(conn));
    printf("Password: %s\n", PQpass(conn));
*/
    return conn;
}

int
data_insert(PGconn *conn, Datum *datum)
{
    PGresult *res;
    char sql[256];

    sprintf(sql, "INSERT INTO IotsData (id_iot, payload) \
                  VALUES (%d, '%s')", \
                  datum->id_iot, datum->payload);

#ifdef DEBUG
    printf("%s\n", sql);
#endif

    res = PQexec(conn, sql);
    PQclear(res);    
 
    return PQresultStatus(res) == PGRES_COMMAND_OK; 
}


Iot *
iot_serialkey_get(PGconn *conn, char *serialkey)
{
    PGresult *res;
    Iot *iot = NULL;
    char sql[256];
    int rows;

    sprintf(sql, "SELECT id, dt, id_local, id_account, name, token \
                  FROM Iots \
                  WHERE token = '%s'", serialkey);

    res = PQexec(conn, sql);    
    rows = PQntuples(res);

    if ( (PQresultStatus(res) == PGRES_TUPLES_OK) && rows ) {
        iot = malloc(sizeof *iot);

        if ( iot != NULL ) {
            iot->id = atoi(PQgetvalue(res, 0, 0));
            sprintf(iot->dt, "%s", PQgetvalue(res, 0, 1));
            iot->id_local = atoi(PQgetvalue(res, 0, 2));
            iot->id_account = atoi(PQgetvalue(res, 0, 3));
            sprintf(iot->name, "%s", PQgetvalue(res, 0, 4));
            sprintf(iot->token, "%s", PQgetvalue(res, 0, 5));
        } else {
            printf("Error malloc\n");
        }
    } else {
        printf("No data retrieved\n");        
    } 

    PQclear(res);
    return iot;
}

