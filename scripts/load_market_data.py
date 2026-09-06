import os
import sys
from datetime import date

from dotenv import load_dotenv

from astraquant.database.repository import get_engine
from astraquant.ingestion.market_data import ingest_market_data
from astraquant.providers.yahoo import YahooFinanceProvider


def main() -> None:
    start_date = (
        date.fromisoformat(sys.argv[1])
        if len(sys.argv) > 1
        else date(2026, 9, 1)
    )

    end_date = (
        date.fromisoformat(sys.argv[2])
        if len(sys.argv) > 2
        else date(2026, 9, 6)
    )

    if start_date >= end_date:
        raise ValueError(
            "start_date must be before end_date"
        )

    load_dotenv()

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured"
        )

    engine = get_engine(database_url)

    provider = YahooFinanceProvider()

    rows = ingest_market_data(
        provider=provider,
        engine=engine,
        exchange="NSE",
        symbol="RELIANCE",
        start_date=start_date,
        end_date=end_date,
        data_source="yahoo_finance",
    )

    print(
        f"Loaded {rows} rows for RELIANCE.NS "
        f"from {start_date} to {end_date}"
    )


if __name__ == "__main__":
    main()
