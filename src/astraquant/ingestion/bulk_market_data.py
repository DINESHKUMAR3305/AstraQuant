from datetime import date

from astraquant.ingestion.market_data import ingest_market_data
from astraquant.providers.base import MarketDataProvider


def ingest_bulk_market_data(
    provider: MarketDataProvider,
    engine,
    securities: list[dict],
    start_date: date,
    end_date: date,
    data_source: str = "yahoo_finance",
) -> dict:
    """Ingest market data for multiple securities."""

    successful = 0
    failed = 0
    total_rows = 0
    failures = []

    for security in securities:
        try:
            rows = ingest_market_data(
                provider=provider,
                engine=engine,
                exchange=security["exchange"],
                symbol=security["symbol"],
                start_date=start_date,
                end_date=end_date,
                data_source=data_source,
            )

            successful += 1
            total_rows += rows

            print(
                f"{security['symbol']}: {rows} rows"
            )

        except Exception as exc:
            failed += 1

            failures.append(
                {
                    "symbol": security["symbol"],
                    "error": str(exc),
                }
            )

            print(
                f"{security['symbol']}: FAILED - {exc}"
            )

    return {
        "successful": successful,
        "failed": failed,
        "total_rows": total_rows,
        "failures": failures,
    }
