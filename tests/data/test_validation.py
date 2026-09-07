import numpy as np
import pandas as pd
import pytest

from astraquant.data.validation import validate_daily_prices


def valid_data():
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2026-01-01", "2026-01-02"]
            ).date,
            "open": [100.0, 101.0],
            "high": [105.0, 106.0],
            "low": [99.0, 100.0],
            "close": [103.0, 104.0],
            "volume": [1000, 1200],
        }
    )


def test_valid_daily_prices():
    valid, rejected = validate_daily_prices(valid_data())

    assert len(valid) == 2
    assert rejected.empty


def test_rejects_nan_values():
    data = valid_data()
    data.loc[0, "close"] = np.nan

    valid, rejected = validate_daily_prices(data)

    assert len(valid) == 1
    assert len(rejected) == 1
    assert rejected.iloc[0]["rejection_reason"] == (
        "OHLCV data contains NaN or infinite values"
    )


def test_rejects_infinite_values():
    data = valid_data()
    data.loc[0, "close"] = np.inf

    valid, rejected = validate_daily_prices(data)

    assert len(valid) == 1
    assert len(rejected) == 1
    assert rejected.iloc[0]["rejection_reason"] == (
        "OHLCV data contains NaN or infinite values"
    )


def test_rejects_non_numeric_price():
    data = valid_data()
    data["close"] = data["close"].astype(object)
    data.loc[0, "close"] = "invalid"

    with pytest.raises(ValueError, match="close must be numeric"):
        validate_daily_prices(data)


def test_rejects_negative_volume():
    data = valid_data()
    data.loc[0, "volume"] = -1

    valid, rejected = validate_daily_prices(data)

    assert len(valid) == 1
    assert len(rejected) == 1
    assert rejected.iloc[0]["rejection_reason"] == (
        "Volume cannot be negative"
    )


def test_rejects_high_lower_than_low():
    data = valid_data()
    data.loc[0, "high"] = 98.0

    valid, rejected = validate_daily_prices(data)

    assert len(valid) == 1
    assert len(rejected) == 1
    assert rejected.iloc[0]["rejection_reason"] == (
        "High price cannot be lower than low price"
    )


def test_rejects_high_lower_than_open():
    data = valid_data()
    data.loc[0, "high"] = 99.0

    valid, rejected = validate_daily_prices(data)

    assert len(valid) == 1
    assert len(rejected) == 1
    assert rejected.iloc[0]["rejection_reason"] == (
        "High price cannot be lower than open price"
    )


def test_rejects_low_higher_than_close():
    data = valid_data()

    data.loc[0, "open"] = 104.0
    data.loc[0, "low"] = 103.5

    valid, rejected = validate_daily_prices(data)

    assert len(valid) == 1
    assert len(rejected) == 1
    assert rejected.iloc[0]["rejection_reason"] == (
        "Low price cannot be higher than close price"
    )
