import pandas as pd
import yfinance as yf

from astraquant.providers.base import MarketDataProvider


class YahooFinanceProvider(MarketDataProvider):
    """Yahoo Finance market-data provider."""

    def fetch_daily_prices(
        self,
        ticker: str,
        period: str = "1mo",
    ) -> pd.DataFrame:
        data = yf.download(
            ticker,
            period=period,
            auto_adjust=False,
            progress=False,
        )

        if data.empty:
            raise ValueError(f"No market data returned for {ticker}")

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data = data.reset_index()
        data.columns = [column.lower() for column in data.columns]

        expected_columns = {
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
        }

        missing = expected_columns - set(data.columns)

        if missing:
            raise ValueError(f"Missing columns: {sorted(missing)}")

        return data[
            ["date", "open", "high", "low", "close", "volume"]
        ]
