
from typing import Protocol

from app.models.enums import Exchange
from app.models.market import MarketQuote


class MarketDataProvider(Protocol):
    async def get_quote(
        self,
        *,
        symbol: str,
        exchange: Exchange,
    ) -> MarketQuote:
        """Return the latest available market quote."""
        ...