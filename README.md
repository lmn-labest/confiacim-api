# Confiacim-api

API web para o confiacim-core.

## Subindo a aplicação com docker

### Desenvolvimento

Subindo aplicação completa com as configurações de desenvolvimento

```bash
docker compose -f docker-compose-dev.yml up -d
```

Esse comando irá subir o `api`, `postgres`, `redis`, `worker_1`, `worker_2` e `flower`.

O api fica disponível em [localhost:8000/](http://localhost:8000/). A documentação em [localhost:8000/docs](http://localhost:8000/docs)
ou [localhost:8000/redoc](http://localhost:8000/redoc). O Flower fica no [localhost:5555](http://localhost:5555)

### Produção

Subindo um aplocação que simula o ambiente de produção.

```bash
docker compose -f docker-compose-prod.yml up -d
```

A agora apenas as dependencias de produção são instaladas na imagem da api. Além disso servidor de aplicação não é mais o `uvicorn` é sim `gunicorn` com 3 `workers`. Também temos `nginx` agindo como proxy reverso para a `api` e `flower`. Todos os serviços estão rodando na rede interna do docker é não tem mais acesso direto externo. A `api` agora fica [localhost:80/](http://localhost:80/) e o `flower` [localhost:80/flower](http://localhost:80/flower).

## Configurando o ambiente de desenvolvimento local

A seguir as instruções Caso você queria trabalhar com o codido da api fora do ambiente docker.

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

O docker compose irá criar dois banco de dados na primeira vez, os `confiacim_api` e `confiacim_api_test`. Essa funcionalidade e provida pelo script [create-databases.sh](./postgres/create-databases.sh). Além disso no `confiacim_api` será criado as tabelas utilizando o script [create_tables.sql](./postgres/create_tables.sql).

Para configurar o banco bastas usar variável de ambiente `DATABASE_URL`.

```bash
export DATABASE_URL="postgresql://confiacim_api_user:confiacim_api_password@localhost:5432/confiacim_api"
```

ou defini-la em um arquivo `.env` como está no aquivo `.env_sample`.

Subindo o redis

```bash
docker compose -f docker-compose-dev.yml up broker -d
```

O `worker`pode ser inicializado locamente com

```bash
watchfiles --filter python 'celery -A confiacim_api.celery worker --concurrency=2  -l INFO'
```

E o serviço `flower` pode se inicializado localmente com:

```bash
celery --broker=redis://localhost:6379/0 flower --port=5555
```

Mas eles tão podem ser inicializados via `docker compose` com:

```bash
docker compose -f docker-compose-dev.yml up worker_1 flower -d
```

Todo os serviços exceto a api pobem ser inicializados via `docker compose` com:

```bash
docker compose -f docker-compose-dev.yml up database borker worker_1 flower
```

Subindo a api com `uvicorn`.

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

Para gerar o a cobertura de testes basta:

```bash
poetry run task tests_report
poetry run task report_server
```

O relátorio fica disponivel no [http://0.0.0.0:8001/](http://0.0.0.0:8001/)


## Atualziando o esquema do banco de dados

Para atualizar o esquema do banco de dados é preciso fazer a modificação necessária no arquivo `create_tables.sql` e gerar uma nova imagem com:

```bash
docker compose -f docker-compose-dev.yml build database
```
