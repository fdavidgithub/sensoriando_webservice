CREATE TABLE Plans (
    id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name        VARCHAR(30) NOT NULL,
    ispublic    BOOLEAN NOT NULL DEFAULT TRUE,
    istrigger   BOOLEAN NOT NULL DEFAULT FALSE,
    retation    INTEGER NOT NULL DEFAULT 1,
    vlhour      FLOAT NOT NULL DEFAULT 0,
    vltrigger   FLOAT NOT NULL DEFAULT 0,
    visible     BOOLEAN NOT NULL DEFAULT TRUE, 

    UNIQUE(name)
);

CREATE TABLE Accounts (
    id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_plan     INTEGER NOT NULL DEFAULT 1 REFERENCES Plans (id),
    username    VARCHAR(20) NOT NULL,
    city        VARCHAR(50) NOT NULL,
    state       VARCHAR(02) NOT NULL,
    country     VARCHAR(02) NOT NULL,
    status      BOOLEAN NOT NULL DEFAULT TRUE,

    UNIQUE(username)
);


/*
 * Central
 */
CREATE TABLE Things (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name        VARCHAR(30) NOT NULL,
    uuid        UUID NOT NULL DEFAULT uuid_generate_v4(), 
    isrelay     BOOLEAN NOT NULL DEFAULT FALSE,

    UNIQUE (uuid)
);

CREATE TABLE ThingsParams (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    key         VARCHAR(20) NOT NULL,
    value       VARCHAR(10) NOT NULL,
    id_thing    INTEGER NOT NULL REFERENCES Things (id),

    UNIQUE(id_thing, key)
);

CREATE TABLE ThingsTags (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_thing    INTEGER NOT NULL REFERENCES Things (id),
    name        VARCHAR(30) NOT NULL,

    UNIQUE(id_thing, name)
);


/* 
 * Relation
 */
CREATE TABLE AccountsThings (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_account  INTEGER NOT NULL REFERENCES Accounts (id),
    id_thing    INTEGER NOT NULL REFERENCES Things (id),

    UNIQUE (id_account, id_thing)
);


/*
 * Sensors
 */
CREATE TABLE Sensors (
	id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	name	    VARCHAR(50) NOT NULL,

    UNIQUE (name)
);

CREATE TABLE SensorsUnits (
	id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	id_sensor   INTEGER NOT NULL REFERENCES Sensors (id),
	name	    VARCHAR(50) NOT NULL,
	initial     VARCHAR(5),
	precision   SMALLINT,
    isdefault   BOOLEAN NOT NULL DEFAULT FALSE,
    expression  VARCHAR(50), --pv: PayloadValue

    UNIQUE (name)
);


/* 
 * Modulation
 */
CREATE TABLE ThingsSensors (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_thing    INTEGER NOT NULL REFERENCES Things (id),
    id_sensor   INTEGER NOT NULL REFERENCES Sensors (id)
);

CREATE TABLE ThingsSensorsParams (
    id              SERIAL NOT NULL PRIMARY KEY,
    dt              TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_thingsensor  INTEGER NOT NULL REFERENCES ThingsSensors (id),
    key             VARCHAR(20) NOT NULL,
    value           VARCHAR(10) NOT NULL,
    
    UNIQUE(id_thingsensor, key)
);

CREATE TABLE ThingsSensorsTags (
    id              SERIAL NOT NULL PRIMARY KEY,
    dt              TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_thingsensor INTEGER NOT NULL REFERENCES ThingsSensors (id),
    name            VARCHAR(30) NOT NULL,
    
    UNIQUE(id_thingsensor, name)
);


/*
 * Iot's data
 */
CREATE TABLE Connections (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    qos         INTEGER NOT NULL,
    retained    BOOLEAN NOT NULL,
    topic       VARCHAR(256) NOT NULL,

    UNIQUE (qos, retained, topic)
);

CREATE TABLE Payloads (
    id              SERIAL NOT NULL PRIMARY KEY,
    dt              TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_connection   INTEGER NOT NULL REFERENCES Connections (id),
    payload	        JSONb NOT NULL,

    UNIQUE (id_connection, payload)
);

CREATE TABLE ThingsSensorsData (
    id              SERIAL NOT NULL PRIMARY KEY,
    dt              TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_payload      INTEGER NOT NULL REFERENCES Payloads (id),
    id_thingsensor  INTEGER NOT NULL REFERENCES ThingsSensors (id),
    dtread          TIMESTAMPTZ NOT NULL,
    value           FLOAT,
    message         VARCHAR(256),
    
    UNIQUE (id_payload, id_thingsensor)
);


