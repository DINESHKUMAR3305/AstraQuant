from datetime import date
from unittest.mock import patch

import pandas as pd

from astraquant.providers.yahoo import YahooFinanceProvider


@patch("astraquant.providers.yahoo.yf.download")
def test_yahoo_provider(mock_download):
    mock_download.return_value = pd.DataFrame(
        {
            "Open": [100.0, 103.0],
            "High": [105.0, 106.0],
            "Low": [99.0, 102.0],
            "Close": [103.0, 105.0],
            "Volume": [100000, 120000],
        },
        index=pd.Index(
            pd.to_datetime(
                ["2026-09-01", "2026-09-02"]
            ),
            name="Date",
        ),
    )

    provider = YahooFinanceProvider()

    data = provider.fetch_daily_prices(
        "RELIANCE.NS",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 3),
    )

    assert len(data) == 2
    assert list(data.columns) == [
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    assert data["close"].tolist() == [
        103.0,
        105.0,
    ]

    mock_download.assert_called_once()
