from datetime import date, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from astraquant.market_calendar import is_nse_trading_day

def get_engine(database_url: str) -> Engine:
    return create_engine(database_url)


def create_company(
    engine: Engine,
    name: str,
    isin: str | None = None,
) -> int:
    query = text("""
        INSERT INTO companies (name, isin)
        VALUES (:name, :isin)
        RETURNING company_id
    """)

    with engine.begin() as connection:
        company_id = connection.execute(
            query,
            {
                "name": name,
                "isin": isin,
            },
        ).scalar_one()

    return company_id


def create_security(
    engine: Engine,
    company_id: int,
    exchange: str,
    symbol: str,
) -> int:
    query = text("""
        INSERT INTO securities (
            company_id,
            exchange,
            symbol
        )
        VALUES (
            :company_id,
            :exchange,
            :symbol
        )
        RETURNING security_id
    """)

    with engine.begin() as connection:
        security_id = connection.execute(
            query,
            {
                "company_id": company_id,
                "exchange": exchange,
                "symbol": symbol,
            },
        ).scalar_one()

    return security_id

def insert_daily_prices(
    engine: Engine,
    security_id: int,
    data,
    data_source: str,
) -> None:
    query = text("""
        INSERT INTO daily_prices (
            security_id,
            trading_date,
            open,
            high,
            low,
            close,
            volume,
            data_source
        )
        VALUES (
            :security_id,
            :trading_date,
            :open,
            :high,
            :low,
            :close,
            :volume,
            :data_source
        )
        ON CONFLICT (security_id, trading_date)
        DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume,
            data_source = EXCLUDED.data_source,
            ingested_at = CURRENT_TIMESTAMP
    """)

    records = [
        {
            "security_id": security_id,
            "trading_date": row.date,
            "open": float(row.open),
            "high": float(row.high),
            "low": float(row.low),
            "close": float(row.close),
            "volume": int(row.volume),
            "data_source": data_source,
        }
        for row in data.itertuples(index=False)
    ]

    with engine.begin() as connection:
        connection.execute(query, records)

def get_security_id(
    engine: Engine,
    exchange: str,
    symbol: str,
) -> int:
    query = text("""
        SELECT security_id
        FROM securities
        WHERE exchange = :exchange
          AND symbol = :symbol
    """)

    with engine.connect() as connection:
        security_id = connection.execute(
            query,
            {
                "exchange": exchange,
                "symbol": symbol,
            },
        ).scalar_one_or_none()

    if security_id is None:
        raise ValueError(
            f"Security not found: {exchange}:{symbol}"
        )

    return security_id

def get_provider_ticker(
    engine: Engine,
    exchange: str,
    symbol: str,
) -> str:
    query = text("""
        SELECT provider_ticker
        FROM securities
        WHERE exchange = :exchange
          AND symbol = :symbol
    """)

    with engine.connect() as connection:
        provider_ticker = connection.execute(
            query,
            {
                "exchange": exchange,
                "symbol": symbol,
            },
        ).scalar_one_or_none()

    if provider_ticker is None:
        raise ValueError(
            f"Provider ticker not found: {exchange}:{symbol}"
        )

    return provider_ticker

def get_all_securities(
    engine: Engine,
) -> list[dict]:
    """Return all securities with provider tickers."""

    query = text("""
        SELECT
            security_id,
            exchange,
            symbol,
            provider_ticker
        FROM securities
        WHERE provider_ticker IS NOT NULL
        ORDER BY security_id
    """)

    with engine.connect() as connection:
        rows = connection.execute(query).mappings().all()

    return [dict(row) for row in rows]


def get_latest_price_date(engine, security_id: int):
    """Return the latest trading date stored for a security."""

    query = text("""
        SELECT MAX(trading_date)
        FROM daily_prices
        WHERE security_id = :security_id
    """)

    with engine.connect() as connection:
        return connection.execute(
            query,
            {"security_id": security_id},
        ).scalar_one()

def has_historical_data_coverage(
    engine,
    security_id: int,
    end_date,
    exchange: str = "NSE",
) -> bool:
    """Return True when data exists through the latest expected trading day."""
    expected_date = end_date - timedelta(days=1)

    if exchange == "NSE":
        while not is_nse_trading_day(expected_date):
            expected_date -= timedelta(days=1)

    query = text("""
        SELECT MAX(trading_date)
        FROM daily_prices
        WHERE security_id = :security_id
    """)

    with engine.connect() as connection:
        latest_date = connection.execute(
            query,
            {"security_id": security_id},
        ).scalar_one()

    if latest_date is None:
        return False

    return latest_date >= expected_date
