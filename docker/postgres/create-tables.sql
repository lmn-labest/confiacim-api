BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> d61d5f077ec5

CREATE TABLE users (
    id SERIAL NOT NULL,
    email VARCHAR(320) NOT NULL,
    password VARCHAR(1024) NOT NULL,
    is_admin BOOLEAN DEFAULT 'false' NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    PRIMARY KEY (id),
    UNIQUE (email)
);

CREATE TABLE simulation (
    id SERIAL NOT NULL,
    tag VARCHAR(30) NOT NULL,
    celery_task_id UUID,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(user_id) REFERENCES users (id),
    UNIQUE (tag)
);

INSERT INTO alembic_version (version_num) VALUES ('d61d5f077ec5') RETURNING alembic_version.version_num;

COMMIT;
