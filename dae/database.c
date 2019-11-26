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
data_insert(PGconn *conn, Data *data)
{
    PGresult *res;
    char sql[256];

    sprintf(sql, "INSERT INTO Data (id_sensor, dt_stream, value, payload) \
                  VALUES (%d, TO_TIMESTAMP('%s', 'YYYYMMDDHH24MISS'), %f, '%s')", \
                  data->id_sensor, data->dt_stream, data->value, data->payload);

#ifdef DEBUG
    printf("%s\n", sql);
#endif

    res = PQexec(conn, sql);
    PQclear(res);    
 
    return PQresultStatus(res) == PGRES_COMMAND_OK; 
}


Sensor *
sensor_serialkey_get(PGconn *conn, char *serialkey)
{
    PGresult *res;
    Sensor *data = NULL;
    char sql[256];
    int rows;

    sprintf(sql, "SELECT id, dt, id_local, id_account, name, token \
                  FROM Iots \
                  WHERE token = '%s'", serialkey);

    res = PQexec(conn, sql);    
    rows = PQntuples(res);

    if ( (PQresultStatus(res) == PGRES_TUPLES_OK) && rows ) {
        data = malloc(sizeof *data);

        if ( data != NULL ) {
            data->id = atoi(PQgetvalue(res, 0, 0));
            sprintf(data->dt, "%s", PQgetvalue(res, 0, 1));
            data->id_local = atoi(PQgetvalue(res, 0, 2));
            data->id_account = atoi(PQgetvalue(res, 0, 3));
            sprintf(data->name, "%s", PQgetvalue(res, 0, 4));
            sprintf(data->serialkey, "%s", PQgetvalue(res, 0, 5));
        } else {
            printf("Error malloc\n");
        }
    } else {
        printf("No data retrieved\n");        
    } 

    PQclear(res);
    return data;
}

