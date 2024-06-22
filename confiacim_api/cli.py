from typing import Annotated, Sequence

import typer
from rich.console import Console
from rich.table import Table
from sqlalchemy import false, select, true

from confiacim_api.database import SessionFactory
from confiacim_api.models import User
from confiacim_api.security import get_password_hash

console = Console()

app = typer.Typer(add_completion=False)


def generate_table(title: str, result: Sequence[User]) -> Table:

    table = Table(title=title)

    table.add_column("Id", justify="center", style="cyan")
    table.add_column("Email", justify="center", style="magenta")
    table.add_column("Is_admin", justify="center", style="magenta")
    table.add_column("Created_at", justify="center", style="magenta")
    table.add_column("Updated_at", justify="center", style="magenta")

    for s in result:
        table.add_row(
            str(s.id),
            s.email,
            str(s.is_admin),
            s.created_at.isoformat() if s.created_at else "None",
            s.updated_at.isoformat() if s.updated_at else "None",
        )

    return table


app_users = typer.Typer()


@app_users.command(name="list")
def list_users(
    admins: Annotated[bool, typer.Option("--admins")] = False,
    users: Annotated[bool, typer.Option("--users")] = False,
):
    """Listando os usuario disponiveis."""
    with SessionFactory() as session:
        stmt = select(User)
        if admins:
            stmt = stmt.where(User.is_admin == true())
        elif users:
            stmt = stmt.where(User.is_admin == false())

        results = session.scalars(stmt).all()

    table = generate_table("Users", results)
    console.print(table)


@app_users.command(name="create-admin")
def create_admin(email: str, password: str):
    """Criando usuário admin."""
    with SessionFactory() as session:

        hashed_password = get_password_hash(password)

        if session.scalar(select(User).where(User.email == email)):
            console.print(f"[red]Admin com o email '{email}' já existe[/red]!")
            raise typer.Exit()

        new_user = User(email=email, password=hashed_password, is_admin=True)

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

    console.print(f"[green]Admin {email} criado com sucesso[/green].")


@app_users.command(name="delete-admin")
def delete_admin(email: str):
    """Deletando usuário admin."""
    with SessionFactory() as session:

        user = session.scalar(
            select(User).where(
                User.email == email,
                User.is_admin == true(),
            )
        )
        if user is None:
            console.print(f"[red]Admin com o email '{email}' não encontrado![/red]")
            raise typer.Exit()

        session.delete(user)
        session.commit()

    console.print(f"[green]Admin com o email '{email}' deletado com sucesso[/green].")


app.add_typer(app_users, name="user", help="Lista os usuarios cadastrados.")
