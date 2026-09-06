import numpy as np
import pandas as pd
import pytest

from astraquant.data.validation import validate_daily_prices


def valid_data():
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2026-09-01", "2026-09-02"]
            ).date,
            "open": [100.0, 102.0],
            "high": [105.0, 107.0],
            "low": [99.0, 101.0],
            "close": [103.0, 106.0],
            "volume": [1000, 1200],
        }
    )


def test_valid_daily_prices():
    validate_daily_prices(valid_data())


def test_rejects_nan_values():
    data = valid_data()
    data.loc[0, "close"] = np.nan

    with pytest.raises(ValueError, match="NaN or infinite"):
        validate_daily_prices(data)


def test_rejects_infinite_values():
    data = valid_data()
    data.loc[0, "close"] = np.inf

    with pytest.raises(ValueError, match="NaN or infinite"):
        validate_daily_prices(data)


def test_rejects_non_numeric_price():
    data = valid_data()
    data["close"] = ["bad", 106.0]

    with pytest.raises(ValueError, match="close must be numeric"):
        validate_daily_prices(data)


def test_rejects_negative_volume():
    data = valid_data()
    data.loc[0, "volume"] = -1

    with pytest.raises(ValueError, match="Volume cannot be negative"):
        validate_daily_prices(data)
