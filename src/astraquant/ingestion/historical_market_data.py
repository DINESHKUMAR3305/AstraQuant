import logging
from datetime import date

from astraquant.database.repository import (
    get_security_id,
    has_historical_data_coverage,
)

from astraquant.ingestion.market_data import (
    NoMarketDataError,
    ingest_historical_market_data,
)
from astraquant.providers.base import MarketDataProvider

logger = logging.getLogger(__name__)


def load_historical_market_data(
    provider: MarketDataProvider,
    engine,
    securities: list[dict],
    start_date: date,
    end_date: date,
    data_source: str = "yahoo_finance",
) -> dict:
    """Load historical market data for a batch of securities."""

    successful = 0
    skipped = 0
    failed = 0
    total_rows = 0
    failures = []

    total_securities = len(securities)

    for index, security in enumerate(securities, start=1):
        symbol = security["symbol"]

        try:
            security_id = get_security_id(
                engine,
                exchange=security["exchange"],
                symbol=symbol,
            )

            if has_historical_data_coverage(
                engine,
                security_id,
                end_date,
                exchange=security["exchange"],
            ):
                skipped += 1

                message = (
                    f"[{index}/{total_securities}] "
                    f"{symbol}: SKIPPED - "
                    "historical data already complete"
                )

                print(message)
                logger.info(message)
                continue

            rows = ingest_historical_market_data(
                provider=provider,
                engine=engine,
                exchange=security["exchange"],
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                data_source=data_source,
            )

            if rows > 0:
                successful += 1
                total_rows += rows

                message = (
                    f"[{index}/{total_securities}] "
                    f"{symbol}: {rows} rows"
                )
            else:
                skipped += 1

                message = (
                    f"[{index}/{total_securities}] "
                    f"{symbol}: SKIPPED - no rows"
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

    return {
        "successful": successful,
        "skipped": skipped,
        "failed": failed,
        "total_rows": total_rows,
        "failures": failures,
    }
