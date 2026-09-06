import yfinance as yf
import pandas as pd


def fetch_daily_prices(ticker: str, period: str = "1mo") -> pd.DataFrame:
    """Fetch daily OHLCV data for an Indian stock."""

    data = yf.download(
        ticker,
        period=period,
        auto_adjust=False,
        progress=False,
    )

    if data.empty:
        raise ValueError(f"No market data returned for {ticker}")

    # yfinance can return MultiIndex columns even for one ticker.
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
        raise ValueError(f"Missing columns: {missing}")

    return data[
        ["date", "open", "high", "low", "close", "volume"]
    ]
