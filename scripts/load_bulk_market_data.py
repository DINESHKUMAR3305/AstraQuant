import logging
import os
import sys
from datetime import date

from dotenv import load_dotenv

from astraquant.database.repository import (
    get_all_securities,
    get_engine,
)
from astraquant.ingestion.bulk_market_data import (
    ingest_bulk_market_data,
    select_securities,
)
from astraquant.providers.yahoo import YahooFinanceProvider


def main():
    load_dotenv()
    load_dotenv("config/market_data.env")

    logging.basicConfig(
        filename="logs/market_data_ingestion.log",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    if len(sys.argv) not in (3, 4, 5):
        raise ValueError(
            "Usage: python scripts/load_bulk_market_data.py "
            "START_DATE END_DATE [LIMIT] [OFFSET]"
        )

    start_date = date.fromisoformat(sys.argv[1])
    end_date = date.fromisoformat(sys.argv[2])

    if start_date >= end_date:
        raise ValueError(
            "START_DATE must be before END_DATE"
        )

    limit = (
        int(sys.argv[3])
        if len(sys.argv) >= 4
        else None
    )

    offset = (
        int(sys.argv[4])
        if len(sys.argv) == 5
        else 0
    )

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
            f"Unsupported market data provider: "
            f"{provider_name}"
        )

    engine = get_engine(database_url)

    all_securities = get_all_securities(engine)
    total_securities = len(all_securities)

    securities = select_securities(
        all_securities,
        limit=limit,
        offset=offset,
    )

    if not securities:
        print(
            f"No securities selected for offset {offset} "
            f"from {total_securities} available securities."
        )
        return

    print(
        f"Processing {len(securities)} securities"
    )
    print(f"Offset:      {offset}")
    print(f"Provider:    {provider_name}")
    print(f"Data source: {data_source}")

    provider = YahooFinanceProvider()

    result = ingest_bulk_market_data(
        provider=provider,
        engine=engine,
        securities=securities,
        start_date=start_date,
        end_date=end_date,
        data_source=data_source,
    )

    print("\nIngestion Summary")
    print("-----------------")
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
