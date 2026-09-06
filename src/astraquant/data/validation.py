import pandas as pd


REQUIRED_COLUMNS = {
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
}


def validate_daily_prices(data: pd.DataFrame) -> None:
    """Validate daily OHLCV market data."""

    missing = REQUIRED_COLUMNS - set(data.columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    if data.empty:
        raise ValueError("Market data is empty")

    if data["date"].duplicated().any():
        raise ValueError("Duplicate trading dates found")

    price_columns = ["open", "high", "low", "close"]

    if (data[price_columns] <= 0).any().any():
        raise ValueError("Prices must be greater than zero")

    if (data["volume"] < 0).any():
        raise ValueError("Volume cannot be negative")

    if (data["high"] < data["low"]).any():
        raise ValueError("High price cannot be lower than low price")

    if (data["high"] < data["open"]).any():
        raise ValueError("High price cannot be lower than open price")

    if (data["high"] < data["close"]).any():
        raise ValueError("High price cannot be lower than close price")

    if (data["low"] > data["open"]).any():
        raise ValueError("Low price cannot be higher than open price")

    if (data["low"] > data["close"]).any():
        raise ValueError("Low price cannot be higher than close price")
