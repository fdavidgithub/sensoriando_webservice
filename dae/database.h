/*
 * POSTGRESQL ACCESSING
 *
 * PGRES_COMMAND_OK
 * Successful completion of a command returning no data.
 *
 * PGRES_TUPLES_OK
 * Successful completion of a command returning data (such as a SELECT or SHOW).
 */
#ifndef DATABASE_H
#define DATABASE_H

#include <libpq-fe.h>

/* 
 * Global 
 */
typedef struct {
    int id;
    char dt[20];
    int user_ptr_id;
    int id_local;
    int id_category;
    char name[30];
    char serialkey[64];
} Sensor;

typedef struct {
    int id;
    char dt[20];
    int id_sensor;
    char dt_stream[20];
    float value;
    char payload[256];
} Data;

/* 
 * Prototypes
 */
void do_exit(PGconn *);
PGconn* do_connect(char *, char *, char *, char *);
Sensor* sensor_serialkey_get(PGconn *, char *);
int data_insert(PGconn *, Data *);

#endif
