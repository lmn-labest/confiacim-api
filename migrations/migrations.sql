BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> f1232937d0c4

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
    base_file BYTEA,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY(user_id) REFERENCES users (id),
    CONSTRAINT case_tag_user UNIQUE (tag, user_id)
);

CREATE TYPE result_status AS ENUM ('CREATED', 'RUNNING', 'FAILED', 'SUCCESS');

CREATE TABLE tencim_results (
    id SERIAL NOT NULL,
    task_id UUID,
    istep INTEGER[],
    t FLOAT[],
    rankine_rc FLOAT[],
    mohr_coulomb_rc FLOAT[],
    error TEXT,
    status result_status,
    case_id INTEGER NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY(case_id) REFERENCES cases (id),
    CONSTRAINT case_task UNIQUE (task_id, case_id)
);

INSERT INTO alembic_version (version_num) VALUES ('f1232937d0c4') RETURNING alembic_version.version_num;

-- Running upgrade f1232937d0c4 -> b2aac65bab92

ALTER TABLE cases ADD COLUMN description TEXT;

UPDATE alembic_version SET version_num='b2aac65bab92' WHERE alembic_version.version_num = 'f1232937d0c4';

-- Running upgrade b2aac65bab92 -> 553a83605190

CREATE TABLE materials_base_case_average_prop (
    id SERIAL NOT NULL,
    "E_c" FLOAT NOT NULL,
    "E_f" FLOAT NOT NULL,
    poisson_c FLOAT NOT NULL,
    poisson_f FLOAT NOT NULL,
    case_id INTEGER NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY(case_id) REFERENCES cases (id),
    UNIQUE (case_id)
);

UPDATE alembic_version SET version_num='553a83605190' WHERE alembic_version.version_num = 'b2aac65bab92';

-- Running upgrade 553a83605190 -> d0d2bbb452e9

CREATE TABLE form_results (
    id SERIAL NOT NULL,
    task_id UUID,
    beta FLOAT,
    resid FLOAT,
    it INTEGER,
    "Pf" FLOAT,
    error TEXT,
    status result_status,
    config JSON,
    case_id INTEGER NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY(case_id) REFERENCES cases (id),
    CONSTRAINT case_task_form_result UNIQUE (task_id, case_id)
);

ALTER TABLE tencim_results DROP CONSTRAINT case_task;

ALTER TABLE tencim_results ADD CONSTRAINT case_task_tencim_result UNIQUE (task_id, case_id);

UPDATE alembic_version SET version_num='d0d2bbb452e9' WHERE alembic_version.version_num = '553a83605190';

-- Running upgrade d0d2bbb452e9 -> 49c45e37ed9a

ALTER TABLE form_results ADD COLUMN critical_point INTEGER;

UPDATE alembic_version SET version_num='49c45e37ed9a' WHERE alembic_version.version_num = 'd0d2bbb452e9';

-- Running upgrade 49c45e37ed9a -> 25b0f40bb3ba

ALTER TABLE tencim_results ADD COLUMN critical_point INTEGER;

UPDATE alembic_version SET version_num='25b0f40bb3ba' WHERE alembic_version.version_num = '49c45e37ed9a';

-- Running upgrade 25b0f40bb3ba -> 097588d1c5ba

ALTER TABLE form_results ADD COLUMN variables_stats JSON;

UPDATE alembic_version SET version_num='097588d1c5ba' WHERE alembic_version.version_num = '25b0f40bb3ba';

-- Running upgrade 097588d1c5ba -> e9fd6582f431

ALTER TABLE form_results ADD COLUMN description TEXT;

ALTER TABLE tencim_results ADD COLUMN description TEXT;

UPDATE alembic_version SET version_num='e9fd6582f431' WHERE alembic_version.version_num = '097588d1c5ba';

-- Running upgrade e9fd6582f431 -> a14583722acf

ALTER TABLE tencim_results ADD COLUMN rc_limit BOOLEAN;

UPDATE alembic_version SET version_num='a14583722acf' WHERE alembic_version.version_num = 'e9fd6582f431';

COMMIT;
