from datetime import date

from astraquant.data.validation import validate_daily_prices
from astraquant.database.repository import (
    get_provider_ticker,
    get_security_id,
    insert_daily_prices,
)
from astraquant.providers.base import MarketDataProvider


def ingest_market_data(
    provider: MarketDataProvider,
    engine,
    exchange: str,
    symbol: str,
    start_date: date,
    end_date: date,
    data_source: str = "yahoo_finance",
) -> int:
    """Fetch, validate, and store market data for one security."""

    if start_date >= end_date:
        raise ValueError(
            "start_date must be before end_date"
        )

    security_id = get_security_id(
        engine,
        exchange=exchange,
        symbol=symbol,
    )

    ticker = get_provider_ticker(
        engine,
        exchange=exchange,
        symbol=symbol,
    )

    data = provider.fetch_daily_prices(
        ticker,
        start_date=start_date,
        end_date=end_date,
    )

    validate_daily_prices(data)

    insert_daily_prices(
        engine,
        security_id=security_id,
        data=data,
        data_source=data_source,
    )

    return len(data)
