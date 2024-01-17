# Confiacim-api

## Configurando o ambiente de desenvolvimento local

Instalando todas as dependencias

```bash
poetry install
```

Para facilitar o processo de desenvolvimento foi utilizado a biblioteca `taskipy`, para vizualiar os comandos disponiveis basta:

```bash
poetry run task -l
```

Subindo o banco de dados POSTGRES via `docker compose`.

```bash
poetry run task up_db
```

O docker compose irá criar dois banco de dados na primeira vez, os `confiacim_api` e `confiacim_api_test`. Essa funcionalidade e provida pelo script[create-databases.sh](./postgres/create-databases.sh). Além disso no `confiacim_api` será criado as tabelas utilizando o scrip [create_tables.sql](./postgres/create_tables.sql).

Para configurar o banco bastas configura a variavel de ambiente `DATABASE_URL`.

```bash
export DATABASE_URL="postgresql://confiacim_api_user:confiacim_api_password@localhost:5432/confiacim_api"
```

ou defini-la em um arquivo `.env` como está no aquivo `.env_sam`.

Subindo a api com `uvicorn`.

```bash
poetry run task server_api
```

O serviço fica disponivel [http://localhost:8000/](http://localhost:8000/). A documentação [http://localhost:8000/docs/](http://localhost:8000/docs/)
ou [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

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
