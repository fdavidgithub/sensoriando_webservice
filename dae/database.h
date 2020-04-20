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
    char uuid[36];
} Thing;

typedef struct {
    int id;
    char dt[20];
    int id_thing;
    char payload[256];
    int qos;
    int retained;
} Datum;

/* 
 * Prototypes
 */
void do_exit(PGconn *);
PGconn* do_connect(char *, char *, char *, char *);
Thing* get_thing_uuid(PGconn *, char *);
int data_insert(PGconn *, Datum *);

#endif
