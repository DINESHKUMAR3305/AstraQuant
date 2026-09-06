import pandas as pd
from datetime import date

from unittest.mock import Mock, patch

from astraquant.ingestion.market_data import ingest_market_data
from astraquant.ingestion.market_data import (
    ingest_historical_market_data,
)

def test_ingest_market_data():
    provider = Mock()
    engine = Mock()

    data = Mock()
    data.__len__ = Mock(return_value=2)

    provider.fetch_daily_prices.return_value = data

    with patch(
        "astraquant.ingestion.market_data.get_security_id",
        return_value=1,
    ), patch(
        "astraquant.ingestion.market_data.get_latest_price_date",
        return_value=None,
    ), patch(
        "astraquant.ingestion.market_data.get_provider_ticker",
        return_value="RELIANCE.NS",
    ), patch(
        "astraquant.ingestion.market_data.validate_daily_prices"
    ), patch(
        "astraquant.ingestion.market_data.insert_daily_prices"
    ):

        result = ingest_market_data(
            provider=provider,
            engine=engine,
            exchange="NSE",
            symbol="RELIANCE",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 6),
        )

    assert result == 2

    provider.fetch_daily_prices.assert_called_once_with(
        "RELIANCE.NS",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 6),
    )


def test_ingest_market_data_retries_after_provider_failure():
    provider = Mock()
    engine = Mock()

    valid_data = Mock()
    valid_data.__len__ = Mock(return_value=2)

    provider.fetch_daily_prices.side_effect = [
        ValueError("temporary failure"),
        valid_data,
    ]

    with patch(
        "astraquant.ingestion.market_data.get_security_id",
        return_value=1,
    ), patch(
        "astraquant.ingestion.market_data.get_latest_price_date",
        return_value=None,
    ), patch(
        "astraquant.ingestion.market_data.get_provider_ticker",
        return_value="RELIANCE.NS",
    ), patch(
        "astraquant.ingestion.market_data.validate_daily_prices"
    ), patch(
        "astraquant.ingestion.market_data.insert_daily_prices"
    ), patch(
        "astraquant.ingestion.market_data.time.sleep"
    ) as mock_sleep:

        result = ingest_market_data(
            provider=provider,
            engine=engine,
            exchange="NSE",
            symbol="RELIANCE",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 6),
        )

    assert result == 2
    assert provider.fetch_daily_prices.call_count == 2
    mock_sleep.assert_called_once_with(2)


def test_ingest_market_data_skips_already_ingested_dates():
    provider = Mock()
    engine = Mock()

    with patch(
        "astraquant.ingestion.market_data.get_security_id",
        return_value=1,
    ), patch(
        "astraquant.ingestion.market_data.get_latest_price_date",
        return_value=date(2026, 9, 4),
    ), patch(
        "astraquant.ingestion.market_data.get_provider_ticker",
        return_value="RELIANCE.NS",
    ):

        result = ingest_market_data(
            provider=provider,
            engine=engine,
            exchange="NSE",
            symbol="RELIANCE",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 4),
        )

    assert result == 0
    provider.fetch_daily_prices.assert_not_called()

def test_ingest_market_data_skips_nse_weekend_before_provider_call():
    provider = Mock()
    engine = Mock()

    with patch(
        "astraquant.ingestion.market_data.get_security_id",
        return_value=1,
    ), patch(
        "astraquant.ingestion.market_data.get_latest_price_date",
        return_value=date(2026, 9, 4),
    ), patch(
        "astraquant.ingestion.market_data.get_provider_ticker",
        return_value="RELIANCE.NS",
    ):

        result = ingest_market_data(
            provider=provider,
            engine=engine,
            exchange="NSE",
            symbol="RELIANCE",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 7),
        )

    assert result == 0
    provider.fetch_daily_prices.assert_not_called()

def test_ingest_historical_market_data_does_not_use_latest_date():
    provider = Mock()
    engine = Mock()

    historical_data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2025-09-01", "2025-09-02"]
            ).date,
            "open": [100.0, 101.0],
            "high": [102.0, 103.0],
            "low": [99.0, 100.0],
            "close": [101.0, 102.0],
            "volume": [1000, 1200],
        }
    )

    provider.fetch_daily_prices.return_value = historical_data

    with patch(
        "astraquant.ingestion.market_data.get_security_id",
        return_value=1,
    ), patch(
        "astraquant.ingestion.market_data.get_provider_ticker",
        return_value="RELIANCE.NS",
    ), patch(
        "astraquant.ingestion.market_data.insert_daily_prices",
    ) as mock_insert:

        result = ingest_historical_market_data(
            provider=provider,
            engine=engine,
            exchange="NSE",
            symbol="RELIANCE",
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 3),
        )

    assert result == 2

    provider.fetch_daily_prices.assert_called_once_with(
        "RELIANCE.NS",
        start_date=date(2025, 9, 1),
        end_date=date(2025, 9, 3),
    )

    mock_insert.assert_called_once()
