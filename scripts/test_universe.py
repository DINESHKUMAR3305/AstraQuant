import os

import pandas as pd
from dotenv import load_dotenv

from astraquant.database.repository import get_engine
from astraquant.universe.loader import load_universe


load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is not configured")

engine = get_engine(database_url)


universe = pd.DataFrame(
    [
        {
            "name": "Reliance Industries Ltd",
            "exchange": "NSE",
            "symbol": "RELIANCE",
            "provider_ticker": "RELIANCE.NS",
        },
        {
            "name": "Tata Consultancy Services Ltd",
            "exchange": "NSE",
            "symbol": "TCS",
            "provider_ticker": "TCS.NS",
        },
        {
            "name": "Infosys Ltd",
            "exchange": "NSE",
            "symbol": "INFY",
            "provider_ticker": "INFY.NS",
        },
    ]
)


load_universe(
    engine=engine,
    data=universe,
)
