from abc import ABC, abstractmethod

import pandas as pd


class MarketDataProvider(ABC):
    """Interface for market-data providers."""

    @abstractmethod
    def fetch_daily_prices(
        self,
        ticker: str,
        period: str = "1mo",
    ) -> pd.DataFrame:
        """Return normalized daily OHLCV data."""
        raise NotImplementedError
