"""Add iteration_infos

Revision ID: d2684f3b1df2
Revises: 374345143513
Create Date: 2024-12-03 19:26:44.951424

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d2684f3b1df2"
down_revision: Union[str, None] = "374345143513"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("form_results", sa.Column("iteration_infos", postgresql.JSON(astext_type=sa.Text()), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("form_results", "iteration_infos")
    # ### end Alembic commands ###