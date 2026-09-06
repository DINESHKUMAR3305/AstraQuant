import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import text

from astraquant.database.repository import (
    get_engine,
    insert_daily_prices,
)


def test_insert_daily_prices():
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured"
        )

    engine = get_engine(database_url)

    with engine.begin() as connection:
        connection.execute(
            text("""
                INSERT INTO companies (name, isin)
                VALUES (:name, :isin)
                ON CONFLICT (isin)
                DO NOTHING
            """),
            {
                "name": "AstraQuant Test Company",
                "isin": "TESTIN000001",
            },
        )

        company_id = connection.execute(
            text("""
                SELECT company_id
                FROM companies
                WHERE isin = :isin
            """),
            {"isin": "TESTIN000001"},
        ).scalar_one()

        connection.execute(
            text("""
                INSERT INTO securities (
                    company_id,
                    exchange,
                    symbol
                )
                VALUES (
                    :company_id,
                    'TEST',
                    'TESTSEC'
                )
                ON CONFLICT (exchange, symbol)
                DO NOTHING
            """),
            {"company_id": company_id},
        )

        security_id = connection.execute(
            text("""
                SELECT security_id
                FROM securities
                WHERE exchange = 'TEST'
                  AND symbol = 'TESTSEC'
            """)
        ).scalar_one()

    data = pd.DataFrame(
        {
            "date": [pd.Timestamp("2026-09-01").date()],
            "open": [100.0],
            "high": [105.0],
            "low": [99.0],
            "close": [103.0],
            "volume": [100000],
        }
    )

    insert_daily_prices(
        engine,
        security_id=security_id,
        data=data,
        data_source="test",
    )

    with engine.connect() as connection:
        row = connection.execute(
            text("""
                SELECT
                    security_id,
                    trading_date,
                    close,
                    volume,
                    data_source,
                    ingested_at
                FROM daily_prices
                WHERE security_id = :security_id
                  AND trading_date = :trading_date
            """),
            {
                "security_id": security_id,
                "trading_date": data.iloc[0]["date"],
            },
        ).one()

    assert row.security_id == security_id
    assert float(row.close) == 103.0
    assert row.volume == 100000
    assert row.data_source == "test"
    assert row.ingested_at is not None

    with engine.begin() as connection:
        connection.execute(
            text("""
                DELETE FROM daily_prices
                WHERE security_id = :security_id
                  AND trading_date = :trading_date
            """),
            {
                "security_id": security_id,
                "trading_date": data.iloc[0]["date"],
            },
        )

        connection.execute(
            text("""
                DELETE FROM securities
                WHERE security_id = :security_id
            """),
            {"security_id": security_id},
        )

        connection.execute(
            text("""
                DELETE FROM companies
                WHERE company_id = :company_id
            """),
            {"company_id": company_id},
        )
