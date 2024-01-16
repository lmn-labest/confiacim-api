\c confiacim_api

CREATE TABLE IF NOT EXISTS Simulation (
    id INTEGER NOT NULL,
    tag VARCHAR(30) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (tag)
);
