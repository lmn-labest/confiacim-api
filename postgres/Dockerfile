FROM postgres:16.1-alpine
COPY create-databases.sh /docker-entrypoint-initdb.d/
COPY create_tables.sql /docker-entrypoint-initdb.d/
