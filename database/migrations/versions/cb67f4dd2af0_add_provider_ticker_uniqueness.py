"""add provider ticker uniqueness

Revision ID: cb67f4dd2af0
Revises: 63537b98ee05
Create Date: 2026-09-06 16:20:17.023998

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb67f4dd2af0'
down_revision: Union[str, Sequence[str], None] = '63537b98ee05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_securities_provider_ticker",
        "securities",
        ["provider_ticker"],
    )

def downgrade() -> None:
    op.drop_constraint(
        "uq_securities_provider_ticker",
        "securities",
        type_="unique",
    )

