from datetime import date
from unittest.mock import Mock

import pandas as pd

from astraquant.ingestion.market_data import ingest_market_data


def test_ingest_market_data():
    provider = Mock()

    provider.fetch_daily_prices.return_value = pd.DataFrame(
        {
            "date": [
                date(2026, 9, 1),
                date(2026, 9, 2),
            ],
            "open": [100.0, 103.0],
            "high": [105.0, 106.0],
            "low": [99.0, 102.0],
            "close": [103.0, 105.0],
            "volume": [100000, 120000],
        }
    )

    engine = Mock()

    import astraquant.ingestion.market_data as market_data

    market_data.get_security_id = Mock(
        return_value=1
    )

    market_data.get_provider_ticker = Mock(
        return_value="RELIANCE.NS"
    )

    market_data.insert_daily_prices = Mock()

    rows = ingest_market_data(
        provider=provider,
        engine=engine,
        exchange="NSE",
        symbol="RELIANCE",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 3),
        data_source="test",
    )

    assert rows == 2

    provider.fetch_daily_prices.assert_called_once_with(
        "RELIANCE.NS",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 3),
    )

    market_data.insert_daily_prices.assert_called_once()
