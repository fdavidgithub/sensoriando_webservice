#ifndef DATABASE_H
#define DATABASE_H

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <sqlite3.h>

#include "block.h"

#define SQL_INSERT "INSERT INTO watter (liters)"
#define SQL_SELECT "SELECT SUM(liters) FROM watter"

#define LEN_SQL 150

struct Db {
    sqlite3 *handle;
    sqlite3_stmt *stmt;

    char *sql;
    char *values;
    char *where;
};

struct Data {
    int id;
    float liters;
};

/*
 * Init pointers and open database
 */
int db_init(struct Db *db, char *dbname)
{
    db->sql = (char *) malloc( sizeof(char) * LEN_SQL );
    db->values = (char *) malloc( sizeof(char) * LEN_SQL );
    db->where = (char *) malloc( sizeof(char) * LEN_SQL );

    return sqlite3_open(dbname, &db->handle);
}

int db_exec(struct Db *db)
{
    return sqlite3_exec(db->handle, db->sql, 0, 0, 0);
}

int db_select(struct Db *db, struct Data *field)
{
    sqlite3_prepare_v2(db->handle, SQL_SELECT, -1, &db->stmt, NULL);
    field->id = 0;

	while (sqlite3_step(db->stmt) != SQLITE_DONE) {
        field->id = 1; //sqlite3_column_int(db->stmt, 0);
        field->liters = sqlite3_column_double(db->stmt, 0);
    }
 
    sqlite3_finalize(db->stmt);
    return field->id;
}

int db_insert(struct Db *db, struct Block *block)
{
    char *values;

    /*
     * Monta SQL
     */
    strcpy(db->sql, SQL_INSERT);
    
    sprintf(db->values, "VALUES (%f)", block->liters);
    strcat(db->sql, db->values);

    return db_exec(db);
}

/*
 * Close db connection
 */
void db_end(struct Db *db)
{
   sqlite3_close(db->handle);
}

#endif

