"""Add market data lineage

Revision ID: e0e0e647909d
Revises: d5d20209c370
Create Date: 2026-09-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e0e0e647909d"
down_revision: Union[str, Sequence[str], None] = "d5d20209c370"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "daily_prices",
        sa.Column(
            "data_source",
            sa.String(length=50),
            nullable=False,
            server_default="unknown",
        ),
    )

    op.add_column(
        "daily_prices",
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    op.drop_column("daily_prices", "ingested_at")
    op.drop_column("daily_prices", "data_source")
