import os

from dotenv import load_dotenv

from astraquant.database.repository import (
    get_engine,
    create_company,
    create_security,
)


load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is not configured")

engine = get_engine(database_url)

company_id = create_company(
    engine,
    name="Reliance Industries Ltd",
)

security_id = create_security(
    engine,
    company_id=company_id,
    exchange="NSE",
    symbol="RELIANCE",
)

print(f"Company ID: {company_id}")
print(f"Security ID: {security_id}")
