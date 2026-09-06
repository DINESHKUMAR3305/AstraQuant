import os
import time
from datetime import date

from dotenv import load_dotenv

from astraquant.data.validation import validate_daily_prices
from astraquant.database.repository import (
    get_provider_ticker,
    get_security_id,
    insert_daily_prices,
)
from astraquant.providers.base import MarketDataProvider


load_dotenv("config/market_data.env")

RETRY_ATTEMPTS = int(os.getenv("MARKET_DATA_RETRY_ATTEMPTS", "3"))
RETRY_DELAY = int(os.getenv("MARKET_DATA_RETRY_DELAY", "2"))


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
        raise ValueError("start_date must be before end_date")

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

    data = None

    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            data = provider.fetch_daily_prices(
                ticker,
                start_date=start_date,
                end_date=end_date,
            )
            break

        except Exception:
            if attempt == RETRY_ATTEMPTS:
                raise

            print(
                f"{symbol}: attempt {attempt}/{RETRY_ATTEMPTS} failed, "
                "retrying..."
            )

            time.sleep(RETRY_DELAY)

    validate_daily_prices(data)

    insert_daily_prices(
        engine,
        security_id=security_id,
        data=data,
        data_source=data_source,
    )

    return len(data)
