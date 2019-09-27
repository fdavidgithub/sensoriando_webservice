/*
 * Example of record
 * 1 CURRENT_TIMESTAMP "Convidado" "Ribeirao Preto" "SP" True True NULL
 */
CREATE TABLE Account (
    user_ptr_id INTEGER NOT NULL PRIMARY KEY,
	dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	city        VARCHAR(50) NOT NULL,
    uf          VARCHAR(02) NOT NULL,
    is_public   BOOLEAN NOT NULL DEFAULT TRUE,
    status      BOOLEAN NOT NULL DEFAULT TRUE,
    dt_status   TIMESTAMP
);

/*
 * Example of record
 * 1 CURRENT_TIMESTAMP "Temperature"
 */
CREATE TABLE Category (
	id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	name	    VARCHAR(50) NOT NULL UNIQUE
);

/*
 * Example of record
 * 1 CURRENT_TIMESTAMP 1 "Kilograma" "C" 2
 */
CREATE TABLE Unit (
	id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	id_category INTEGER NOT NULL REFERENCES Category (id),
	name	    VARCHAR(50) NOT NULL UNIQUE,
	initial     VARCHAR(5),
	precision   SMALLINT
);

/*
 * Example of record
 * 1 CURRENT_TIMESTAMP "Bloco" 1
 */
CREATE TABLE Local (
	id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	name	    VARCHAR(50) NOT NULL,
	user_ptr_id	INTEGER NOT NULL,

	UNIQUE (name, user_ptr_id)
);

/*
 * Example of record
 * 1 CURRENT_TIMESTAMP 1 1 1 "Apart" 
 */
CREATE TABLE Sensor (
	id          SERIAL NOT NULL PRIMARY KEY,
    	dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    	user_ptr_id INTEGER NOT NULL,
    	id_local    INTEGER NOT NULL REFERENCES Local (id),
    	id_unit     INTEGER NOT NULL REFERENCES Unit (id),
   	name        VARCHAR(30) NOT NULL,
    	token       VARCHAR(32) NOT NULL UNIQUE DEFAULT MD5(random()::text)
);

/*
 * Example of record
 * 1 CURRENT_TIMESTAMP 1 "DHT11"
 */
CREATE TABLE Flag (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_sensor   INTEGER NOT NULL REFERENCES Sensor (id),
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
    id_sensor   INTEGER NOT NULL REFERENCES Sensor (id),
    payload	JSONb NOT NULL,

    UNIQUE (id_sensor, payload)
);

