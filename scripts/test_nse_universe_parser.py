import os

from dotenv import load_dotenv

from astraquant.database.repository import get_engine
from astraquant.providers.nse.universe import (
    load_nse_universe_file,
)
from astraquant.universe.loader import load_universe


load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is not configured")

engine = get_engine(database_url)


data = load_nse_universe_file(
    "data/raw/nse/test_universe.csv"
)

load_universe(
    engine=engine,
    data=data.rename(
        columns={
            "company_name": "name",
        }
    ),
)

print(data.to_string(index=False))
