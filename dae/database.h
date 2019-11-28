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
    int id_local;
    int id_account;
    char name[30];
    char token[64];
} Iot;

typedef struct {
    int id;
    char dt[20];
    int id_iot;
    char payload[256];
} Datum;

/* 
 * Prototypes
 */
void do_exit(PGconn *);
PGconn* do_connect(char *, char *, char *, char *);
Iot* iot_serialkey_get(PGconn *, char *);
int data_insert(PGconn *, Datum *);

#endif
