"""Initial migration

Revision ID: f1232937d0c4
Revises:
Create Date: 2024-08-04 14:39:15.307317

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f1232937d0c4"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password", sa.String(length=1024), nullable=False),
        sa.Column("is_admin", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tag", sa.String(length=30), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("base_file", sa.LargeBinary(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tag", "user_id", name="case_tag_user"),
    )
    op.create_table(
        "tencim_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=True),
        sa.Column("istep", postgresql.ARRAY(sa.Integer(), as_tuple=True), nullable=True),
        sa.Column("t", postgresql.ARRAY(sa.Float(), as_tuple=True), nullable=True),
        sa.Column("rankine_rc", postgresql.ARRAY(sa.Float(), as_tuple=True), nullable=True),
        sa.Column("mohr_coulomb_rc", postgresql.ARRAY(sa.Float(), as_tuple=True), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum("CREATED", "RUNNING", "FAILED", "SUCCESS", name="result_status"), nullable=True),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["cases.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_id", "case_id", name="case_task"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("tencim_results")
    op.drop_table("cases")
    op.drop_table("users")
    # ### end Alembic commands ###
