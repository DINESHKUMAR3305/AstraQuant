from abc import ABC, abstractmethod
from datetime import date

import pandas as pd


class MarketDataProvider(ABC):
    """Interface for market-data providers."""

    @abstractmethod
    def fetch_daily_prices(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> pd.DataFrame:
        """Return normalized daily OHLCV data."""
        raise NotImplementedError
