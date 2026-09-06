from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "symbol",
    "name_of_company",
    "series",
    "date_of_listing",
    "paid_up_value",
    "market_lot",
    "isin_number",
    "face_value",
}


def load_nse_universe_file(
    file_path: str | Path,
) -> pd.DataFrame:
    """Load and normalize the NSE equity security master."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"NSE universe file not found: {path}"
        )

    data = pd.read_csv(path)

    # Normalize NSE column names.
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
        [
            "symbol",
            "name_of_company",
            "series",
            "date_of_listing",
            "paid_up_value",
            "market_lot",
            "isin_number",
            "face_value",
        ]
    ].copy()

    # Initial AstraQuant universe: normal NSE equity series.
    data = data[
        data["series"].astype(str).str.upper() == "EQ"
    ].copy()

    # Convert listing date to a Python date.
    data["date_of_listing"] = pd.to_datetime(
        data["date_of_listing"],
        format="%d-%b-%Y",
        errors="raise",
    ).dt.date

    # Normalize text fields.
    data["symbol"] = (
        data["symbol"].astype(str).str.strip()
    )

    data["name_of_company"] = (
        data["name_of_company"].astype(str).str.strip()
    )

    data["series"] = (
        data["series"].astype(str).str.strip()
    )

    data["isin_number"] = (
        data["isin_number"].astype(str).str.strip()
    )

    # NSE is the exchange.
    data["exchange"] = "NSE"

    # Yahoo Finance provider ticker.
    data["provider_ticker"] = (
        data["symbol"] + ".NS"
    )

    return data[
        [
            "name_of_company",
            "exchange",
            "symbol",
            "provider_ticker",
            "isin_number",
            "series",
            "date_of_listing",
            "paid_up_value",
            "market_lot",
            "face_value",
        ]
    ]
