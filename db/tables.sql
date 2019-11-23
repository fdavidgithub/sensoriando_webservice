/*
 * Example of record
 * 1 CURRENT_TIMESTAMP "Convidado" "Ribeirao Preto" "SP" True True NULL
 */
CREATE TABLE Accounts (
    id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	city        VARCHAR(50) NOT NULL,
    uf          VARCHAR(02) NOT NULL,
    ispublic    BOOLEAN NOT NULL DEFAULT TRUE,
    status      BOOLEAN NOT NULL DEFAULT TRUE
);

/*
 * Example of record
 * 1 CURRENT_TIMESTAMP "Temperature"
 */
CREATE TABLE Categories (
	id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	name	    VARCHAR(50) NOT NULL UNIQUE
);

/*
 * Example of record
 * 1 CURRENT_TIMESTAMP 1 "Kilograma" "C" 2
 */
CREATE TABLE Units (
	id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	id_category INTEGER NOT NULL REFERENCES Categories (id),
	name	    VARCHAR(50) NOT NULL UNIQUE,
	initial     VARCHAR(5),
	precision   SMALLINT
);

/*
 * Example of record
 * 1 CURRENT_TIMESTAMP "Bloco" 1
 */
CREATE TABLE Locals (
	id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	name	    VARCHAR(50) NOT NULL,
	id_account	INTEGER NOT NULL,
    id_local    INTEGER,

	UNIQUE (id_account, name, id_local)
);

/*
 * Example of record
 * 1 CURRENT_TIMESTAMP 1 1 1 "Apart" 
 */
CREATE TABLE Sensors (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_account  INTEGER NOT NULL REFERENCES Accounts (id),
    id_local    INTEGER NOT NULL REFERENCES Locals (id),
    id_unit     INTEGER NOT NULL REFERENCES Units (id),
   	name        VARCHAR(30) NOT NULL,
    token       VARCHAR(32) NOT NULL UNIQUE DEFAULT MD5(random()::text),
    adjustement FLOAT NOT NULL DEFAULT 0,

    UNIQUE (id_account, name)
);

/*
 * Example of record
 * 1 CURRENT_TIMESTAMP "suppy power" "220" 1
 */
CREATE TABLE Params (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    key         VARCHAR(20) NOT NULL,
    value       VARCHAR(10) NOT NULL,
    id_sensor   INTEGER NOT NULL REFERENCES Sensors (id),

    UNIQUE(id_sensor, key)
);

/*
 * Example of record
 * 1 CURRENT_TIMESTAMP 1 "DHT11"
 */
CREATE TABLE Flags (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_sensor   INTEGER NOT NULL REFERENCES Sensors (id),
    name        VARCHAR(30) NOT NULL,

    UNIQUE(id_sensor, name)
);

/*
 * Example of record
 * 1 CURRENT_TIMESTAMP 1 "{{token:}{dt:}{value:}}"
 */
CREATE TABLE Data (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_sensor   INTEGER NOT NULL REFERENCES Sensors (id),
    payload	    JSONb NOT NULL,

    UNIQUE (id_sensor, payload)
);


