import numpy as np
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

    if data["date"].isna().any():
        raise ValueError("Trading dates cannot be null")

    if data["date"].duplicated().any():
        raise ValueError("Duplicate trading dates found")

    price_columns = ["open", "high", "low", "close"]
    numeric_columns = price_columns + ["volume"]

    for column in numeric_columns:
        if not pd.api.types.is_numeric_dtype(data[column]):
            raise ValueError(f"{column} must be numeric")

    if not np.isfinite(data[numeric_columns].to_numpy()).all():
        raise ValueError("OHLCV data contains NaN or infinite values")

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
