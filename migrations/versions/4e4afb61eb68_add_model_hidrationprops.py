"""Add model HidrationProps

Revision ID: 4e4afb61eb68
Revises: bf6ce47c0449
Create Date: 2024-11-20 16:08:07.340206

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "4e4afb61eb68"
down_revision: Union[str, None] = "bf6ce47c0449"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "hidration_prop_infos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("E_c_t", postgresql.ARRAY(sa.Float(), as_tuple=True), nullable=True),
        sa.Column("E_c_values", postgresql.ARRAY(sa.Float(), as_tuple=True), nullable=True),
        sa.Column("poisson_c_t", postgresql.ARRAY(sa.Float(), as_tuple=True), nullable=True),
        sa.Column("poisson_c_values", postgresql.ARRAY(sa.Float(), as_tuple=True), nullable=True),
        sa.Column("cohesion_c_t", postgresql.ARRAY(sa.Float(), as_tuple=True), nullable=True),
        sa.Column("cohesion_c_values", postgresql.ARRAY(sa.Float(), as_tuple=True), nullable=True),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["cases.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_id", name="case_hidration_prop"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("hidration_prop_infos")
    # ### end Alembic commands ###
