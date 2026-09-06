import os

from dotenv import load_dotenv

from astraquant.data.validation import validate_daily_prices
from astraquant.database.repository import (
    get_engine,
    get_provider_ticker,
    get_security_id,
    insert_daily_prices,
)
from astraquant.providers.base import MarketDataProvider
from astraquant.providers.yahoo import YahooFinanceProvider


def load_market_data(
    provider: MarketDataProvider,
    exchange: str,
    symbol: str,
    period: str = "5d",
) -> None:
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    engine = get_engine(database_url)

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
        period=period,
    )

    validate_daily_prices(data)

    insert_daily_prices(
        engine,
        security_id=security_id,
        data=data,
    )

    print(f"Loaded {len(data)} rows for {ticker}")


if __name__ == "__main__":
    provider = YahooFinanceProvider()

    load_market_data(
        provider=provider,
        exchange="NSE",
        symbol="RELIANCE",
    )
