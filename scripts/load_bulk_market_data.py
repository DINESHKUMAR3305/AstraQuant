import os
import sys
from datetime import date

from dotenv import load_dotenv

from astraquant.database.repository import get_all_securities, get_engine
from astraquant.ingestion.bulk_market_data import ingest_bulk_market_data
from astraquant.providers.yahoo import YahooFinanceProvider


def main():
    if len(sys.argv) not in (3, 4):
        raise ValueError(
                "Usage: python scripts/load_bulk_market_data.py START_DATE END_DATE [LIMIT]"
                )
    start_date = date.fromisoformat(sys.argv[1])
    end_date = date.fromisoformat(sys.argv[2])

    limit = int(sys.argv[3]) if len(sys.argv) == 4 else None

    if start_date >= end_date:
        raise ValueError("START_DATE must be before END_DATE")

    load_dotenv()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    engine = get_engine(database_url)

    securities = get_all_securities(engine)

    if limit is not None:
        securities = securities[:limit]
    print(f"Processing {len(securities)} securities")

    provider = YahooFinanceProvider()

    result = ingest_bulk_market_data(
        provider=provider,
        engine=engine,
        securities=securities,
        start_date=start_date,
        end_date=end_date,
        data_source="yahoo_finance",
    )

    print("\nIngestion Summary")
    print("-----------------")
    print(f"Successful: {result['successful']}")
    print(f"Failed:     {result['failed']}")
    print(f"Total rows: {result['total_rows']}")

    if result["failures"]:
        print("\nFailures:")
        for failure in result["failures"]:
            print(f"- {failure['symbol']}: {failure['error']}")


if __name__ == "__main__":
    main()
