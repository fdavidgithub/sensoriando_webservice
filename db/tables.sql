CREATE TABLE Accounts (
    id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    username    VARCHAR(20) NOT NULL,
    city        VARCHAR(50) NOT NULL,
    state       VARCHAR(02) NOT NULL,
    country     VARCHAR(02) NOT NULL,
    ispublic    BOOLEAN NOT NULL DEFAULT TRUE,
    status      BOOLEAN NOT NULL DEFAULT TRUE,
    usetrigger  BOOLEAN NOT NULL DEFAULT FALSE,

    UNIQUE(username)
);

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
    expression  VARCHAR(255) NOT NULL DEFAULT 'pv', --pv: PayloadValue

    UNIQUE (id_sensor, name)
);

CREATE TABLE SensorsParams (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    key         VARCHAR(20) NOT NULL,
    value       VARCHAR(10) NOT NULL,
    id_sensor   INTEGER NOT NULL REFERENCES Sensors (id),

    UNIQUE(id_sensor, key)
);

CREATE TABLE ThingsData (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_thing    INTEGER NOT NULL REFERENCES Things (id),
    id_sensor   INTEGER NOT NULL REFERENCES Sensors (id),
    qos         INTEGER NOT NULL,
    retained    BOOLEAN NOT NULL,
    payload	    JSONb NOT NULL,

    UNIQUE (id_thing, id_sensor, payload)
);

CREATE TABLE AccountsThings (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_account  INTEGER NOT NULL REFERENCES Accounts (id),
    id_thing    INTEGER NOT NULL REFERENCES Things (id),

    UNIQUE (id_account, id_thing)
);


