from datetime import date
from unittest.mock import Mock, patch

from astraquant.ingestion.historical_market_data import (
    load_historical_market_data,
)
from astraquant.ingestion.market_data import NoMarketDataError


SECURITIES = [
    {
        "exchange": "NSE",
        "symbol": "AAA",
    },
    {
        "exchange": "NSE",
        "symbol": "BBB",
    },
]


def test_historical_loader_counts_successful_rows():
    provider = Mock()
    engine = Mock()

    with patch(
        "astraquant.ingestion.historical_market_data"
        ".ingest_historical_market_data",
        return_value=100,
    ):
        result = load_historical_market_data(
            provider=provider,
            engine=engine,
            securities=SECURITIES[:1],
            start_date=date(2025, 9, 1),
            end_date=date(2026, 9, 1),
        )

    assert result["successful"] == 1
    assert result["skipped"] == 0
    assert result["failed"] == 0
    assert result["total_rows"] == 100


def test_historical_loader_counts_no_market_data_as_skipped():
    provider = Mock()
    engine = Mock()

    with patch(
        "astraquant.ingestion.historical_market_data"
        ".ingest_historical_market_data",
        side_effect=NoMarketDataError("No market data"),
    ):
        result = load_historical_market_data(
            provider=provider,
            engine=engine,
            securities=SECURITIES[:1],
            start_date=date(2025, 9, 1),
            end_date=date(2026, 9, 1),
        )

    assert result["successful"] == 0
    assert result["skipped"] == 1
    assert result["failed"] == 0
    assert result["total_rows"] == 0


def test_historical_loader_continues_after_failure():
    provider = Mock()
    engine = Mock()

    with patch(
        "astraquant.ingestion.historical_market_data"
        ".ingest_historical_market_data",
        side_effect=[
            RuntimeError("Provider failure"),
            50,
        ],
    ):
        result = load_historical_market_data(
            provider=provider,
            engine=engine,
            securities=SECURITIES,
            start_date=date(2025, 9, 1),
            end_date=date(2026, 9, 1),
        )

    assert result["successful"] == 1
    assert result["skipped"] == 0
    assert result["failed"] == 1
    assert result["total_rows"] == 50

    assert result["failures"] == [
        {
            "symbol": "AAA",
            "error": "Provider failure",
        }
    ]
