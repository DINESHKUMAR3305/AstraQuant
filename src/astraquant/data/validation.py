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


def validate_daily_prices(
    data: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separate valid OHLCV rows from rejected rows."""

    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    if data.empty:
        raise ValueError("Market data is empty")

    data = data.copy()

    rejection_reason = pd.Series("", index=data.index, dtype="object")

    def reject(mask, reason):
        """Assign a rejection reason only to rows not already rejected."""
        mask = mask & rejection_reason.eq("")
        rejection_reason.loc[mask] = reason

    reject(
        data["date"].isna(),
        "Trading date cannot be null",
    )

    numeric_columns = ["open", "high", "low", "close", "volume"]

    for column in numeric_columns:
        if not pd.api.types.is_numeric_dtype(data[column]):
            raise ValueError(f"{column} must be numeric")

    numeric_values = data[numeric_columns].to_numpy()

    reject(
        ~np.isfinite(numeric_values).all(axis=1),
        "OHLCV data contains NaN or infinite values",
    )

    price_columns = ["open", "high", "low", "close"]

    reject(
        (data[price_columns] <= 0).any(axis=1),
        "Prices must be greater than zero",
    )

    reject(
        data["volume"] < 0,
        "Volume cannot be negative",
    )

    reject(
        data["high"] < data["low"],
        "High price cannot be lower than low price",
    )

    reject(
        data["high"] < data["open"],
        "High price cannot be lower than open price",
    )

    reject(
        data["high"] < data["close"],
        "High price cannot be lower than close price",
    )

    reject(
        data["low"] > data["open"],
        "Low price cannot be higher than open price",
    )

    reject(
        data["low"] > data["close"],
        "Low price cannot be higher than close price",
    )

    reject(
        data["date"].duplicated(keep=False),
        "Duplicate trading date found",
    )

    rejected_mask = rejection_reason != ""

    valid_data = data.loc[~rejected_mask].copy()
    rejected_data = data.loc[rejected_mask].copy()

    rejected_data["rejection_reason"] = rejection_reason.loc[
        rejected_mask
    ].values

    return valid_data, rejected_data
