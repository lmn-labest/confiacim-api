BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 4c4ff3149075

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

CREATE TABLE cases (
    id SERIAL NOT NULL,
    tag VARCHAR(30) NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(user_id) REFERENCES users (id),
    UNIQUE (tag)
);

INSERT INTO alembic_version (version_num) VALUES ('4c4ff3149075') RETURNING alembic_version.version_num;

-- Running upgrade 4c4ff3149075 -> 804fd92d2ad4

ALTER TABLE cases DROP CONSTRAINT cases_tag_key;

ALTER TABLE cases ADD CONSTRAINT case_tag_user UNIQUE (tag, user_id);

UPDATE alembic_version SET version_num='804fd92d2ad4' WHERE alembic_version.version_num = '4c4ff3149075';

-- Running upgrade 804fd92d2ad4 -> 7bb0922230d5

ALTER TABLE cases ADD COLUMN base_file BYTEA;

UPDATE alembic_version SET version_num='7bb0922230d5' WHERE alembic_version.version_num = '804fd92d2ad4';

-- Running upgrade 7bb0922230d5 -> ff0116c0539e

CREATE TABLE tencim_results (
    id SERIAL NOT NULL,
    task_id UUID,
    istep INTEGER[],
    t FLOAT[],
    rankine_rc FLOAT[],
    mohr_coulomb_rc FLOAT[],
    error TEXT,
    case_id INTEGER NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY(case_id) REFERENCES cases (id),
    CONSTRAINT case_task UNIQUE (task_id, case_id)
);

UPDATE alembic_version SET version_num='ff0116c0539e' WHERE alembic_version.version_num = '7bb0922230d5';

-- Running upgrade ff0116c0539e -> ce65ed45d626

ALTER TABLE cases ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now();

ALTER TABLE cases ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now();

UPDATE alembic_version SET version_num='ce65ed45d626' WHERE alembic_version.version_num = 'ff0116c0539e';

-- Running upgrade ce65ed45d626 -> 368fdacf6a3e

CREATE TYPE result_status AS ENUM ('RUNNING', 'FAILED', 'SUCCESS');

ALTER TABLE tencim_results ADD COLUMN status result_status;

UPDATE alembic_version SET version_num='368fdacf6a3e' WHERE alembic_version.version_num = 'ce65ed45d626';

COMMIT;
