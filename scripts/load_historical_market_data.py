import logging
import os
import sys
from datetime import date

from dotenv import load_dotenv

from astraquant.database.repository import (
    get_all_securities,
    get_engine,
)
from astraquant.ingestion.bulk_market_data import select_securities
from astraquant.ingestion.historical_market_data import (
    load_historical_market_data,
)
from astraquant.providers.yahoo import YahooFinanceProvider

logger = logging.getLogger(__name__)


def main():
    load_dotenv()
    load_dotenv("config/market_data.env")

    logging.basicConfig(
        filename="logs/historical_market_data.log",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    start_date = date.fromisoformat(
        os.environ["HISTORICAL_START_DATE"]
    )
    end_date = date.fromisoformat(
        os.environ["HISTORICAL_END_DATE"]
    )

    batch_size = int(
        os.getenv("HISTORICAL_BATCH_SIZE", "25")
    )

    offset = int(sys.argv[1]) if len(sys.argv) >= 2 else 0

    if len(sys.argv) > 2:
        raise ValueError(
            "Usage: python scripts/load_historical_market_data.py [OFFSET]"
        )

    if start_date >= end_date:
        raise ValueError(
            "HISTORICAL_START_DATE must be before "
            "HISTORICAL_END_DATE"
        )

    if batch_size <= 0:
        raise ValueError(
            "HISTORICAL_BATCH_SIZE must be greater than zero"
        )

    if offset < 0:
        raise ValueError("OFFSET cannot be negative")

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured"
        )

    provider_name = os.getenv(
        "MARKET_DATA_PROVIDER",
        "yahoo_finance",
    )

    data_source = os.getenv(
        "MARKET_DATA_SOURCE",
        "yahoo_finance",
    )

    if provider_name != "yahoo_finance":
        raise ValueError(
            f"Unsupported market data provider: {provider_name}"
        )

    engine = get_engine(database_url)

    all_securities = get_all_securities(engine)

    securities = select_securities(
        all_securities,
        limit=batch_size,
        offset=offset,
    )

    if not securities:
        print(
            f"No securities selected for offset {offset} "
            f"from {len(all_securities)} available securities."
        )
        return

    print(
        f"Processing {len(securities)} securities"
    )
    print(
        f"Date range: {start_date} → {end_date}"
    )
    print(f"Batch size: {batch_size}")
    print(f"Offset:     {offset}")
    print(f"Provider:   {provider_name}")
    print(f"Data source: {data_source}")

    provider = YahooFinanceProvider()

    result = load_historical_market_data(
        provider=provider,
        engine=engine,
        securities=securities,
        start_date=start_date,
        end_date=end_date,
        data_source=data_source,
    )

    print("\nHistorical Ingestion Summary")
    print("----------------------------")
    print(f"Successful: {result['successful']}")
    print(f"Skipped:    {result['skipped']}")
    print(f"Failed:     {result['failed']}")
    print(f"Total rows: {result['total_rows']}")

    if result["failures"]:
        print("\nFailures:")

        for failure in result["failures"]:
            print(
                f"- {failure['symbol']}: "
                f"{failure['error']}"
            )


if __name__ == "__main__":
    main()
