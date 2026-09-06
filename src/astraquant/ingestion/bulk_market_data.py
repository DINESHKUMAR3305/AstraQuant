import logging
from datetime import date

from astraquant.ingestion.market_data import ingest_market_data
from astraquant.providers.base import MarketDataProvider
from astraquant.ingestion.market_data import (
    NoMarketDataError,
    ingest_market_data,
)

logger = logging.getLogger(__name__)


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
    skipped = 0
    total_rows = 0
    failures = []

    total_securities = len(securities)

    for index, security in enumerate(securities, start=1):
        symbol = security["symbol"]

        try:
            rows = ingest_market_data(
                provider=provider,
                engine=engine,
                exchange=security["exchange"],
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                data_source=data_source,
            )

            successful += 1
            total_rows += rows

            message = (
                f"[{index}/{total_securities}] "
                f"{symbol}: {rows} rows"
            )

            print(message)
            logger.info(message)
            
        except NoMarketDataError as exc:
            skipped += 1

            message = (
                f"[{index}/{total_securities}] "
                f"{symbol}: SKIPPED - {exc}"
            )

            print(message)
            logger.info(message)

        except Exception as exc:
            failed += 1

            failure = {
                "symbol": symbol,
                "error": str(exc),
            }

            failures.append(failure)

            message = (
                f"[{index}/{total_securities}] "
                f"{symbol}: FAILED - {exc}"
            )

            print(message)
            logger.error(message)

    summary = {
        "successful": successful,
        "failed": failed,
        "skipped": skipped,
        "total_rows": total_rows,
        "failures": failures,
    }

    logger.info(
        "Ingestion completed: successful=%s failed=%s total_rows=%s",
        successful,
        failed,
        total_rows,
    )

    return summary
