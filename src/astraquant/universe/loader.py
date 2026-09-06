import pandas as pd

from sqlalchemy import text
from sqlalchemy.engine import Engine


REQUIRED_COLUMNS = {
    "name",
    "exchange",
    "symbol",
    "provider_ticker",
}


def validate_universe(data: pd.DataFrame) -> None:
    """Validate stock universe data."""

    missing = REQUIRED_COLUMNS - set(data.columns)

    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}"
        )

    if data.empty:
        raise ValueError("Universe data is empty")

    if data["symbol"].duplicated().any():
        raise ValueError("Duplicate symbols found")

    if data["provider_ticker"].duplicated().any():
        raise ValueError("Duplicate provider tickers found")

    if data["name"].isna().any():
        raise ValueError("Company name cannot be empty")

    if data["exchange"].isna().any():
        raise ValueError("Exchange cannot be empty")

    if data.duplicated(
            subset=["exchange", "symbol"]
    ).any():
        raise ValueError("Duplicate exchange and symbol combinations found" )

    if data["provider_ticker"].isna().any():
        raise ValueError("Provider ticker cannot be empty")


def load_universe(
    engine: Engine,
    data: pd.DataFrame,
) -> None:
    """Load companies and securities into PostgreSQL."""

    validate_universe(data)

    with engine.begin() as connection:
        for row in data.itertuples(index=False):

            company_id = connection.execute(
                text("""
                    SELECT company_id
                    FROM companies
                    WHERE name = :name
                """),
                {"name": row.name},
            ).scalar_one_or_none()

            if company_id is None:
                company_id = connection.execute(
                    text("""
                        INSERT INTO companies (name)
                        VALUES (:name)
                        RETURNING company_id
                    """),
                    {"name": row.name},
                ).scalar_one()

            existing_security = connection.execute(
                text("""
                    SELECT security_id
                    FROM securities
                    WHERE exchange = :exchange
                      AND symbol = :symbol
                """),
                {
                    "exchange": row.exchange,
                    "symbol": row.symbol,
                },
            ).scalar_one_or_none()

            if existing_security is None:
                connection.execute(
                    text("""
                        INSERT INTO securities (
                            company_id,
                            exchange,
                            symbol,
                            provider_ticker
                        )
                        VALUES (
                            :company_id,
                            :exchange,
                            :symbol,
                            :provider_ticker
                        )
                    """),
                    {
                        "company_id": company_id,
                        "exchange": row.exchange,
                        "symbol": row.symbol,
                        "provider_ticker": row.provider_ticker,
                    },
                )

    print(f"Loaded {len(data)} universe records")
