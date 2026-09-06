from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "symbol",
    "company_name",
}


def load_nse_universe_file(
    file_path: str | Path,
) -> pd.DataFrame:
    """Load an NSE universe CSV and normalize its columns."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"NSE universe file not found: {path}"
        )

    data = pd.read_csv(path)

    data.columns = [
        column.strip().lower().replace(" ", "_")
        for column in data.columns
    ]

    missing = REQUIRED_COLUMNS - set(data.columns)

    if missing:
        raise ValueError(
            f"Missing NSE columns: {sorted(missing)}"
        )

    data = data[
        ["symbol", "company_name"]
    ].copy()

    data["exchange"] = "NSE"

    data["provider_ticker"] = (
        data["symbol"].astype(str) + ".NS"
    )

    return data[
        [
            "company_name",
            "exchange",
            "symbol",
            "provider_ticker",
        ]
    ]
