from astraquant.providers.nse.universe import (
    load_nse_universe_file,
)


def test_load_nse_universe_file():
    data = load_nse_universe_file(
        "data/raw/nse/EQUITY_L.csv"
    )

    assert not data.empty

    assert len(data) == 2288

    assert set(data["exchange"]) == {"NSE"}
    assert set(data["series"]) == {"EQ"}

    assert data["symbol"].is_unique
    assert data["isin_number"].is_unique
    assert data["provider_ticker"].is_unique

    assert data["date_of_listing"].notna().all()

    expected_columns = {
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
    }

    assert set(data.columns) == expected_columns
