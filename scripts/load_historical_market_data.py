import argparse
import logging
import os

from datetime import date

from dotenv import load_dotenv

from astraquant.database.repository import (
    get_all_securities,
    get_engine,
)
from astraquant.ingestion.bulk_market_data import (
    iter_security_batches,
)
from astraquant.ingestion.historical_market_data import (
    load_historical_market_data,
)
from astraquant.providers.yahoo import YahooFinanceProvider


logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Load historical market data for NSE securities."
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of securities to process.",
    )

    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Number of securities to skip before processing.",
    )

    return parser.parse_args()


def main():
    load_dotenv()
    load_dotenv("config/market_data.env")

    logging.basicConfig(
        filename="logs/historical_market_data.log",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    args = parse_args()

    start_date = date.fromisoformat(
        os.environ["HISTORICAL_START_DATE"]
    )

    end_date = date.fromisoformat(
        os.environ["HISTORICAL_END_DATE"]
    )

    batch_size = int(
        os.getenv("HISTORICAL_BATCH_SIZE", "25")
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

    if args.limit is not None and args.limit <= 0:
        raise ValueError(
            "--limit must be greater than zero"
        )

    if args.offset < 0:
        raise ValueError(
            "--offset cannot be negative"
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
            f"Unsupported market data provider: {provider_name}"
        )

    engine = get_engine(database_url)

    all_securities = get_all_securities(engine)

    selected_securities = all_securities[args.offset:]

    if args.limit is not None:
        selected_securities = selected_securities[:args.limit]

    if not selected_securities:
        print(
            f"No securities selected for offset {args.offset} "
            f"from {len(all_securities)} available securities."
        )
        return

    print(f"Total securities: {len(all_securities)}")
    print(f"Processing:       {len(selected_securities)}")
    print(f"Date range:       {start_date} → {end_date}")
    print(f"Batch size:       {batch_size}")
    print(f"Offset:           {args.offset}")
    print(f"Provider:         {provider_name}")
    print(f"Data source:      {data_source}")

    provider = YahooFinanceProvider()

    overall_successful = 0
    overall_skipped = 0
    overall_failed = 0
    overall_rows = 0
    overall_failures = []

    for batch_number, batch in enumerate(
        iter_security_batches(
            selected_securities,
            batch_size=batch_size,
        ),
        start=1,
    ):
        print(
            f"\n=== Batch {batch_number} "
            f"({len(batch)} securities) ==="
        )

        result = load_historical_market_data(
            provider=provider,
            engine=engine,
            securities=batch,
            start_date=start_date,
            end_date=end_date,
            data_source=data_source,
        )

        overall_successful += result["successful"]
        overall_skipped += result["skipped"]
        overall_failed += result["failed"]
        overall_rows += result["total_rows"]
        overall_failures.extend(result["failures"])

        print(
            f"Batch {batch_number} summary: "
            f"successful={result['successful']} "
            f"skipped={result['skipped']} "
            f"failed={result['failed']} "
            f"rows={result['total_rows']}"
        )

    print("\nHistorical Ingestion Summary")
    print("----------------------------")
    print(f"Successful: {overall_successful}")
    print(f"Skipped:    {overall_skipped}")
    print(f"Failed:     {overall_failed}")
    print(f"Total rows: {overall_rows}")

    if overall_failures:
        print("\nFailures:")

        for failure in overall_failures:
            print(
                f"- {failure['symbol']}: "
                f"{failure['error']}"
            )


if __name__ == "__main__":
    main()
