def postgresql_connection_url(*, user: str, password: str, host: str, db_name: str, port: int = 5432) -> str:
    """Gera a string de conexão para o postgres"""
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}"


def sentinel_connection_url(*, host: str, password: str | None = None, port: int = 26379) -> str:
    """Gera a string de conexão para o sentinel"""
    if password:
        return f"sentinel://:{password}@{host}:{port}"
    return f"sentinel://{host}:{port}"
