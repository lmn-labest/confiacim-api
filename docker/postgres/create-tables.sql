\c confiacim_api

CREATE TABLE IF NOT EXISTS simulation (
    id SERIAL NOT NULL,
    tag VARCHAR(30) NOT NULL,
    celery_task_id UUID,
    PRIMARY KEY (id),
    UNIQUE (tag)
);
