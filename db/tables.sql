CREATE TABLE Accounts (
    id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	city        VARCHAR(50) NOT NULL,
    uf          VARCHAR(02) NOT NULL,
    ispublic    BOOLEAN NOT NULL DEFAULT TRUE,
    status      BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE AccountsLocals (
	id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	name	    VARCHAR(50) NOT NULL,
	id_account	INTEGER NOT NULL,
    id_local    INTEGER NOT NULL DEFAULT 0,

	UNIQUE (id_account, name, id_local)
);

CREATE TABLE Categories (
	id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	name	    VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE CategoriesUnits (
	id          SERIAL NOT NULL PRIMARY KEY,
	dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	id_category INTEGER NOT NULL REFERENCES Categories (id),
	name	    VARCHAR(50) NOT NULL UNIQUE,
	initial     VARCHAR(5),
	precision   SMALLINT
);

CREATE TABLE Iots (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_account  INTEGER NOT NULL REFERENCES Accounts (id),
    id_local    INTEGER NOT NULL REFERENCES AccountsLocals (id),
   	name        VARCHAR(30) NOT NULL,
    token       VARCHAR(32) NOT NULL UNIQUE DEFAULT MD5(random()::text),

    UNIQUE (id_account, name)
);

CREATE TABLE IotsSensors (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_iot      INTEGER NOT NULL REFERENCES Iots (id),
    id_unit     INTEGER NOT NULL REFERENCES CategoriesUnits (id),
    factor      FLOAT NOT NULL DEFAULT 0,

    UNIQUE (id_iot, id_unit)
);

CREATE TABLE IotsParams (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    key         VARCHAR(20) NOT NULL,
    value       VARCHAR(10) NOT NULL,
    id_iot      INTEGER NOT NULL REFERENCES Iots (id),

    UNIQUE(id_iot, key)
);

CREATE TABLE IotsFlags (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_iot      INTEGER NOT NULL REFERENCES Iots (id),
    name        VARCHAR(30) NOT NULL,

    UNIQUE(id_iot, name)
);

CREATE TABLE IotsData (
    id          SERIAL NOT NULL PRIMARY KEY,
    dt          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_iot      INTEGER NOT NULL REFERENCES Iots (id),
    payload	    JSONb NOT NULL,

    UNIQUE (id_iot, payload)
);


