import pandas as pd

from sqlalchemy import text
from sqlalchemy.engine import Engine


REQUIRED_COLUMNS = {
    "name_of_company",
    "exchange",
    "symbol",
    "provider_ticker",
    "isin_number",
    "series",
    "date_of_listing",
    "paid_up_value",
    "market_lot",
    "face_value",
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

    # Exchange + symbol must uniquely identify a security.
    if data.duplicated(
        subset=["exchange", "symbol"]
    ).any():
        raise ValueError(
            "Duplicate exchange and symbol combinations found"
        )

    # ISIN should uniquely identify a security.
    if data["isin_number"].duplicated().any():
        raise ValueError(
            "Duplicate ISIN numbers found"
        )

    # Provider tickers must be unique.
    if data["provider_ticker"].duplicated().any():
        raise ValueError(
            "Duplicate provider tickers found"
        )

    if data["name_of_company"].isna().any():
        raise ValueError(
            "Company name cannot be empty"
        )

    if data["exchange"].isna().any():
        raise ValueError(
            "Exchange cannot be empty"
        )

    if data["symbol"].isna().any():
        raise ValueError(
            "Symbol cannot be empty"
        )

    if data["provider_ticker"].isna().any():
        raise ValueError(
            "Provider ticker cannot be empty"
        )

    if data["isin_number"].isna().any():
        raise ValueError(
            "ISIN cannot be empty"
        )

    if (~data["series"].eq("EQ")).any():
        raise ValueError(
            "Universe contains non-EQ securities"
        )

    if (~data["exchange"].eq("NSE")).any():
        raise ValueError(
            "Universe contains non-NSE securities"
        )

    if (data["market_lot"] <= 0).any():
        raise ValueError(
            "Market lot must be greater than zero"
        )

    if (data["paid_up_value"] <= 0).any():
        raise ValueError(
            "Paid-up value must be greater than zero"
        )

    if (data["face_value"] <= 0).any():
        raise ValueError(
            "Face value must be greater than zero"
        )


def load_universe(
    engine: Engine,
    data: pd.DataFrame,
) -> None:
    """Load companies and securities into PostgreSQL."""

    validate_universe(data)

    inserted = 0
    updated = 0

    with engine.begin() as connection:
        for row in data.itertuples(index=False):

            # Find company by ISIN first.
            company_id = connection.execute(
                text("""
                    SELECT company_id
                    FROM companies
                    WHERE isin = :isin
                """),
                {
                    "isin": row.isin_number,
                },
            ).scalar_one_or_none()

            # If not found by ISIN, try company name.
            if company_id is None:
                company_id = connection.execute(
                    text("""
                        SELECT company_id
                        FROM companies
                        WHERE name = :name
                    """),
                    {
                        "name": row.name_of_company,
                    },
                ).scalar_one_or_none()

            # Create company if it doesn't exist.
            if company_id is None:
                company_id = connection.execute(
                    text("""
                        INSERT INTO companies (
                            name,
                            isin
                        )
                        VALUES (
                            :name,
                            :isin
                        )
                        RETURNING company_id
                    """),
                    {
                        "name": row.name_of_company,
                        "isin": row.isin_number,
                    },
                ).scalar_one()

            else:
                # Keep company metadata synchronized.
                connection.execute(
                    text("""
                        UPDATE companies
                        SET
                            name = :name,
                            isin = :isin
                        WHERE company_id = :company_id
                    """),
                    {
                        "name": row.name_of_company,
                        "isin": row.isin_number,
                        "company_id": company_id,
                    },
                )

            # Find the security.
            security_id = connection.execute(
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

            if security_id is None:

                # Insert new security.
                connection.execute(
                    text("""
                        INSERT INTO securities (
                            company_id,
                            exchange,
                            symbol,
                            provider_ticker,
                            isin,
                            series,
                            listing_date,
                            paid_up_value,
                            market_lot,
                            face_value
                        )
                        VALUES (
                            :company_id,
                            :exchange,
                            :symbol,
                            :provider_ticker,
                            :isin,
                            :series,
                            :listing_date,
                            :paid_up_value,
                            :market_lot,
                            :face_value
                        )
                    """),
                    {
                        "company_id": company_id,
                        "exchange": row.exchange,
                        "symbol": row.symbol,
                        "provider_ticker": row.provider_ticker,
                        "isin": row.isin_number,
                        "series": row.series,
                        "listing_date": row.date_of_listing,
                        "paid_up_value": row.paid_up_value,
                        "market_lot": row.market_lot,
                        "face_value": row.face_value,
                    },
                )

                inserted += 1

            else:

                # Update existing security.
                connection.execute(
                    text("""
                        UPDATE securities
                        SET
                            company_id = :company_id,
                            provider_ticker = :provider_ticker,
                            isin = :isin,
                            series = :series,
                            listing_date = :listing_date,
                            paid_up_value = :paid_up_value,
                            market_lot = :market_lot,
                            face_value = :face_value
                        WHERE security_id = :security_id
                    """),
                    {
                        "company_id": company_id,
                        "provider_ticker": row.provider_ticker,
                        "isin": row.isin_number,
                        "series": row.series,
                        "listing_date": row.date_of_listing,
                        "paid_up_value": row.paid_up_value,
                        "market_lot": row.market_lot,
                        "face_value": row.face_value,
                        "security_id": security_id,
                    },
                )

                updated += 1

    print(f"Inserted securities: {inserted}")
    print(f"Updated securities: {updated}")
    print(f"Processed universe records: {len(data)}")
