from alembic import op
import sqlalchemy as sa


revision = "f7805d61dcd3"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("company_id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("cin", sa.String(21), nullable=True, unique=True),
        sa.Column("isin", sa.String(12), nullable=True, unique=True),
        sa.Column("sector", sa.String(100), nullable=True),
        sa.Column("industry", sa.String(150), nullable=True),
    )

    op.create_table(
        "securities",
        sa.Column("security_id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "company_id",
            sa.BigInteger(),
            sa.ForeignKey("companies.company_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("exchange", sa.String(10), nullable=False),
        sa.Column("symbol", sa.String(50), nullable=False),
        sa.UniqueConstraint("exchange", "symbol"),
    )

    op.create_table(
        "daily_prices",
        sa.Column(
            "security_id",
            sa.BigInteger(),
            sa.ForeignKey("securities.security_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("trading_date", sa.Date(), nullable=False),
        sa.Column("open", sa.Numeric(18, 6), nullable=False),
        sa.Column("high", sa.Numeric(18, 6), nullable=False),
        sa.Column("low", sa.Numeric(18, 6), nullable=False),
        sa.Column("close", sa.Numeric(18, 6), nullable=False),
        sa.Column("adjusted_close", sa.Numeric(18, 6), nullable=True),
        sa.Column("volume", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("security_id", "trading_date"),
    )

    op.create_table(
        "corporate_actions",
        sa.Column("action_id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "security_id",
            sa.BigInteger(),
            sa.ForeignKey("securities.security_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("action_date", sa.Date(), nullable=False),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("ratio", sa.String(50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("corporate_actions")
    op.drop_table("daily_prices")
    op.drop_table("securities")
    op.drop_table("companies")
