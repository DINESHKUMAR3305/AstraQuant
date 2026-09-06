from astraquant.providers.nse.universe import (
    load_nse_universe_file,
)
from astraquant.universe.loader import validate_universe


data = load_nse_universe_file(
    "data/raw/nse/EQUITY_L.csv"
)

validate_universe(data)

print("NSE universe validation: OK")
print(f"Validated securities: {len(data)}")
