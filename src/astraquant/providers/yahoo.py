from datetime import date

import pandas as pd
import yfinance as yf

from astraquant.providers.base import MarketDataProvider


class YahooFinanceProvider(MarketDataProvider):
    def fetch_daily_prices(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> pd.DataFrame:
        """Fetch normalized daily OHLCV data from Yahoo Finance."""

        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
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

        data["date"] = pd.to_datetime(data["date"]).dt.date

        data = data[
            (data["date"] >= start_date)
            & (data["date"] < end_date)
        ].copy()

        if data.empty:
            raise ValueError(
                f"No market data returned for {ticker} "
                f"within requested range {start_date} to {end_date}"
            )

        return data[
            ["date", "open", "high", "low", "close", "volume"]
        ]
