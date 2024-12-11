import pytest
from sqlalchemy import select
from typer.testing import CliRunner

from confiacim_api.cli import app as cli
from confiacim_api.models import User


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def session_cli(mocker, session):
    return mocker.patch("confiacim_api.cli.SessionFactory", return_value=session)


@pytest.mark.cli
def test_list_users_all_columns(runner, session_cli, users: list[User]):

    result = runner.invoke(cli, ["user", "list"])

    assert result.exit_code == 0

    stdout = result.stdout

    assert "Id" in stdout
    assert "Email" in stdout
    assert "Is_admin" in stdout
    assert "Created_at" in stdout
    assert "Updated_at" in stdout


@pytest.mark.cli
def test_list_users_all(runner, session_cli, users: list[User]):

    result = runner.invoke(cli, ["user", "list"])

    assert result.exit_code == 0

    stdout = result.stdout

    for u in users:
        assert str(u.id) in stdout


@pytest.mark.cli
def test_list_users_only_admins(runner, session_cli, users: list[User]):

    result = runner.invoke(cli, ["user", "list", "--admins"])

    assert result.exit_code == 0

    stdout = result.stdout

    assert "False" not in stdout

    assert str(users[2].id) in stdout
    assert "True" in stdout


@pytest.mark.cli
def test_list_users_only_users(runner, session_cli, users: list[User]):

    result = runner.invoke(cli, ["user", "list", "--admins"])

    assert result.exit_code == 0

    stdout = result.stdout

    assert "False" not in stdout

    assert str(users[2].id) in stdout
    assert "True" in stdout


@pytest.mark.cli
def test_create_admin_user(runner, session_cli):

    result = runner.invoke(cli, ["user", "create-admin", "admin@admin.com", "123456"])

    assert result.exit_code == 0

    with session_cli() as session:
        user = session.scalar(select(User))

    assert user

    assert user.email == "admin@admin.com"
    assert user.password != "123456"
    assert user.is_admin is True

    assert "Admin admin@admin.com criado com sucesso." in result.stdout


@pytest.mark.cli
def test_negative_create_admin_user_email_have_be_unique(
    runner,
    session_cli,
    admin_user,
):

    result = runner.invoke(
        cli,
        [
            "user",
            "create-admin",
            admin_user.email,
            "123456",
        ],
    )

    assert result.exit_code == 0

    with session_cli() as session:
        users = session.scalars(select(User)).all()

    assert len(users) == 1

    assert f"Admin com o email '{admin_user.email}' já existe!" in result.stdout


@pytest.mark.cli
def test_delete_admin(runner, session_cli, admin_user):

    result = runner.invoke(
        cli,
        [
            "user",
            "delete-admin",
            admin_user.email,
        ],
    )

    assert result.exit_code == 0

    with session_cli() as session:
        user = session.get(User, admin_user.id)

    assert user is None

    assert f"Admin com o email '{admin_user.email}' deletado com sucesso." in result.stdout


@pytest.mark.cli
def test_negative_delete_admin_user_not_found(runner, session_cli):

    result = runner.invoke(
        cli,
        [
            "user",
            "delete-admin",
            "not_found@admin.com",
        ],
    )

    assert result.exit_code == 0

    assert "Admin com o email 'not_found@admin.com' não encontrado!" in result.stdout


@pytest.mark.cli
def test_negative_delete_admin_user_must_be_admin(runner, session_cli, user):

    result = runner.invoke(cli, ["user", "delete-admin", user.email])

    with session_cli() as session:
        assert session.get(User, user.id).id == user.id

    assert result.exit_code == 0

    assert f"Admin com o email '{user.email}' não encontrado!" in result.stdout
