"""Add status in tencim results

Revision ID: 368fdacf6a3e
Revises: ce65ed45d626
Create Date: 2024-08-04 00:24:08.440271

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from confiacim_api.models import ResultStatus

# revision identifiers, used by Alembic.
revision: str = "368fdacf6a3e"
down_revision: Union[str, None] = "ce65ed45d626"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    post_status = postgresql.ENUM(ResultStatus, name="result_status")
    post_status.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "tencim_results",
        sa.Column("status", sa.Enum("RUNNING", "FAILED", "SUCCESS", name="result_status"), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    ResultStatus.create(op.get_bind(), checkfirst=True)
    op.drop_column("tencim_results", "status")
    # ### end Alembic commands ###