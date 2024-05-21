BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 01124ddc640a

CREATE TABLE simulation (
    id SERIAL NOT NULL,
    tag VARCHAR(30) NOT NULL,
    celery_task_id UUID,
    PRIMARY KEY (id),
    UNIQUE (tag)
);

INSERT INTO alembic_version (version_num) VALUES ('01124ddc640a') RETURNING alembic_version.version_num;

COMMIT;
