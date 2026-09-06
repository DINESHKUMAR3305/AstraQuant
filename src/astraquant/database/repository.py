from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


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
) -> None:
    query = text("""
        INSERT INTO daily_prices (
            security_id,
            trading_date,
            open,
            high,
            low,
            close,
            volume
        )
        VALUES (
            :security_id,
            :trading_date,
            :open,
            :high,
            :low,
            :close,
            :volume
        )
        ON CONFLICT (security_id, trading_date)
        DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume
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
