from datetime import date
from unittest.mock import Mock, patch

from astraquant.ingestion.market_data import ingest_market_data


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
