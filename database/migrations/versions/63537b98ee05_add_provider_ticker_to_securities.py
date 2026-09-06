from alembic import op
import sqlalchemy as sa


revision = "63537b98ee05"
down_revision = "f7805d61dcd3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "securities",
        sa.Column("provider_ticker", sa.String(50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("securities", "provider_ticker")
