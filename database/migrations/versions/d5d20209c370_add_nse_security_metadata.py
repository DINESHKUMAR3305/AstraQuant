from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d5d20209c370"
down_revision: Union[str, Sequence[str], None] = "cb67f4dd2af0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "securities",
        sa.Column("isin", sa.String(12), nullable=True),
    )

    op.add_column(
        "securities",
        sa.Column("series", sa.String(10), nullable=True),
    )

    op.add_column(
        "securities",
        sa.Column("listing_date", sa.Date(), nullable=True),
    )

    op.add_column(
        "securities",
        sa.Column(
            "paid_up_value",
            sa.Numeric(18, 6),
            nullable=True,
        ),
    )

    op.add_column(
        "securities",
        sa.Column(
            "market_lot",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "securities",
        sa.Column(
            "face_value",
            sa.Numeric(18, 6),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("securities", "face_value")
    op.drop_column("securities", "market_lot")
    op.drop_column("securities", "paid_up_value")
    op.drop_column("securities", "listing_date")
    op.drop_column("securities", "series")
    op.drop_column("securities", "isin")
