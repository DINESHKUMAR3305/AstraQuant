import os

from dotenv import load_dotenv

from astraquant.database.repository import (
    get_engine,
    get_security_id,
)

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is not configured")

engine = get_engine(database_url)

security_id = get_security_id(
    engine,
    exchange="NSE",
    symbol="RELIANCE",
)

print(f"RELIANCE security ID: {security_id}")
