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
    char name[30];
    char uuid[36];
} Thing;

typedef struct {
    int id;
    char dt[20];
    char payload[256];
    int qos;
    int retained;
    char topic[256];
} Payload;

/* 
 * Prototypes
 */
void do_exit(PGconn *);
PGconn* do_connect(char *, char *, char *, char *);
Thing* get_thing_uuid(PGconn *, char *);
int payload_insert(PGconn *, Payload *);

#endif
