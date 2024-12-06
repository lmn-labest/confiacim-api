# Confiacim-api

API web para o `confiacim-core`.

![arquitetura](./docs/img/confiacim_web.drawio.png)

Figura 1: Arquitetura básica

## Subindo a aplicação com docker

### Desenvolvimento

Subindo aplicação completa com as configurações de desenvolvimento

```bash
docker compose -f docker-compose-dev.yml up -d
```

Esse comando irá subir o `api`, `postgres`, `boker`, `worker` e `flower`.

 - `api` ➡️ [localhost:8000/](http://localhost:8000/api/)
 - `doc` ➡️ [localhost:8000/api/docs](http://localhost:8000/api/docs)
 - `Flower` ➡️ [localhost:5555/flower/](http://localhost:5555/flower/)

### Produção

Subindo um aplocação que simula o ambiente de produção.

```bash
docker compose up -d
```

A agora apenas as dependencias de produção são instaladas na imagem da `api`. Além disso servidor de aplicação não é mais o `uvicorn` é sim `gunicorn` com `3 workers`. Todos os serviços estão rodando na rede interna do docker e não tem mais acesso direto externo. Exceto pelo `nginx` agindo como proxy reverso para a `api` e `flower`.

- `doc` ➡️ [localhost:80/docs](http://localhost:80/api/docs)
- `api` ➡️ [localhost:80/](http://localhost:80/api/)
- `Flower` ➡️ [localhost:80/flower](http://localhost:80/flower/)

Lembrando que a porta `80` pode ser omitida

## Configurando o ambiente de desenvolvimento local

A seguir as instruções caso você queria trabalhar com o códido da `api` fora do ambiente `docker`.

Instalando todas as dependencias

```bash
poetry install
```

Para facilitar o processo de desenvolvimento foi utilizado a biblioteca `taskipy`, para vizualiar os comandos disponiveis basta:

```bash
poetry run task -l
```

Subindo o banco de dados `POSTGRES` via `docker compose`.

```bash
docker compose -f docker-compose-dev.yml up database -d
```

O docker compose irá criar dois banco de dados na primeira vez, os `confiacim_api` e `confiacim_api_test`. Essa funcionalidade e provida pelo script [create-databases.sh](./postgres/create-databases.sh).

Para configurar o banco bastas usar variável de ambiente `CONFIACIM_API_DATABASE_URL`.

```bash
export CONFIACIM_API_DATABASE_URL="postgresql://confiacim_api_user:confiacim_api_password@localhost:5432/confiacim_api"
```

ou defini-la em um arquivo `.env` como está no arquivo de exemplo `.env_sample`.

Subindo o redis

```bash
docker compose -f docker-compose-dev.yml up redis-master sentinel -d
```

O `worker` pode ser inicializado locamente com

```bash
watchfiles --filter python 'celery -A confiacim_api.celery worker --concurrency=2  -l INFO'
```

E o serviço `flower` pode se inicializado localmente com:

```bash
celery --broker=redis://localhost:6379/0 flower --port=5555
```

Mas eles tão podem ser inicializados via `docker compose` com:

```bash
docker compose -f docker-compose-dev.yml up worker flower -d
```

Todo os serviços exceto a `api` pobem ser inicializados via `docker compose` com:

```bash
docker compose -f docker-compose-dev.yml up database borker worker flower
```

ou simplesmente com:

```bash
task up_services
```

Subindo a api com `uvicorn`.

```bash
uvicorn confiacim_api.app:app --reload
```

ou com

```bash
poetry run task server_api
```

## Teste, formatadores e linters

Para essas tarefas foram utilizados `black`, `ruff`, `mypy` e `pytest`.

Para chamar os formatadores, linter e testes

```bash
poetry run task fmt
poetry run task linter
poetry run task tests
```

Os teste serão automaticamente rodados utilizando o DB `confiacim_api_test`.

Para gerar a cobertura de testes basta:

```bash
poetry run task tests_report
poetry run task report_server
```

O relátorio fica disponivel no [http://0.0.0.0:8001/](http://0.0.0.0:8001/)


## Deploy na Petrobras

Para gerar o arquivo requirements.txt necessario basta:

```bash
poetry export > requirements.txt
```

Depois é preciso alter manualmente entrada do `confiacim` para algo como:

```bash
confiacim @ file:./packages/confiacim-0.12.0a0-py3-none-any.whl ; python_version >= "3.11" and python_version < "3.12" \
```

### Migrações do banco de dados offline

No ambiente Petrobras não podemos usar o `Almebic` para aplicar as migrações. Para contonar essa limitação foi usado modo offline. Nesse modo é gerado um arquivo `.sql` com todas a migrações necessarias que depois são aplicadas manualmente no `DB`.

```bash
alembic upgrade head --sql > migrations/migrations.sql
```

```sql
GRANT USAGE ON SCHEMA "a17790" TO "a17790_aplicacao";
GRANT SELECT ON ALL TABLES IN SCHEMA "a17790" TO "a17790_aplicacao";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA "a17790" TO "a17790_aplicacao";
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA "a17790" TO "a17790_aplicacao";
GRANT UPDATE ON ALL SEQUENCES IN SCHEMA "a17790" TO "a17790_aplicacao";
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA "a17790" TO "a17790_aplicacao";
GRANT CONNECT ON DATABASE "a17790t" TO "a17790_aplicacao";
```
