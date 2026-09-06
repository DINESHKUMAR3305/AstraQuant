from datetime import date
from unittest.mock import Mock, patch

from astraquant.ingestion.bulk_market_data import ingest_bulk_market_data


def test_ingest_bulk_market_data_continues_after_failure():
    provider = Mock()
    engine = Mock()

    securities = [
        {"exchange": "NSE", "symbol": "RELIANCE"},
        {"exchange": "NSE", "symbol": "INVALID"},
        {"exchange": "NSE", "symbol": "TCS"},
    ]

    with patch(
        "astraquant.ingestion.bulk_market_data.ingest_market_data",
        side_effect=[2, ValueError("test failure"), 3],
    ) as mock_ingest:

        result = ingest_bulk_market_data(
            provider=provider,
            engine=engine,
            securities=securities,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 6),
        )

    assert result["successful"] == 2
    assert result["failed"] == 1
    assert result["total_rows"] == 5

    assert result["failures"] == [
        {
            "symbol": "INVALID",
            "error": "test failure",
        }
    ]

    assert mock_ingest.call_count == 3
