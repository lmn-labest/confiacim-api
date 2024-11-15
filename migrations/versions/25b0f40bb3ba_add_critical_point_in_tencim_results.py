"""Add critical point in tencim results

Revision ID: 25b0f40bb3ba
Revises: 49c45e37ed9a
Create Date: 2024-10-06 20:43:25.940598

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "25b0f40bb3ba"
down_revision: Union[str, None] = "49c45e37ed9a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("tencim_results", sa.Column("critical_point", sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("tencim_results", "critical_point")
    # ### end Alembic commands ###
