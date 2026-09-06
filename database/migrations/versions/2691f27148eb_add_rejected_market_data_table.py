"""add rejected market data table"""

from alembic import op
import sqlalchemy as sa

revision = "2691f27148eb"
down_revision = "e0e0e647909d"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rejected_market_data",
        sa.Column("security_id", sa.BigInteger(), nullable=False),
        sa.Column("trading_date", sa.Date(), nullable=False),
        sa.Column("open", sa.Numeric(20, 6), nullable=False),
        sa.Column("high", sa.Numeric(20, 6), nullable=False),
        sa.Column("low", sa.Numeric(20, 6), nullable=False),
        sa.Column("close", sa.Numeric(20, 6), nullable=False),
        sa.Column("volume", sa.BigInteger(), nullable=False),
        sa.Column("data_source", sa.String(50), nullable=False),
        sa.Column("rejection_reason", sa.Text(), nullable=False),
        sa.Column(
            "rejected_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["security_id"],
            ["securities.security_id"],
        ),
        sa.PrimaryKeyConstraint("security_id", "trading_date"),
    )

def downgrade():
    op.drop_index(
        "ix_rejected_market_data_security_date",
        table_name="rejected_market_data",
    )
    op.drop_table("rejected_market_data")
