from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from app.models.enums import (
    Currency,
    Exchange,
    MarketDataStatus,
)
from app.models.market import MarketQuote


TWOPLACES = Decimal("0.01")


QUOTE_FIXTURES = {
    "RELIANCE": {
        "price": "2984.35",
        "previous_close": "2950.10",
        "open": "2960.00",
        "day_high": "3002.40",
        "day_low": "2942.15",
        "volume": 8_450_320,
    },
    "TCS": {
        "price": "4215.60",
        "previous_close": "4178.25",
        "open": "4190.00",
        "day_high": "4236.80",
        "day_low": "4162.10",
        "volume": 2_140_550,
    },
    "INFY": {
        "price": "1824.75",
        "previous_close": "1808.40",
        "open": "1812.20",
        "day_high": "1836.90",
        "day_low": "1799.50",
        "volume": 5_920_180,
    },
}


class DeterministicMarketDataProvider:
    name = "deterministic-market-provider"

    async def get_quote(
        self,
        *,
        symbol: str,
        exchange: Exchange,
    ) -> MarketQuote:
        normalized_symbol = symbol.strip().upper()

        fixture = QUOTE_FIXTURES.get(
            normalized_symbol
        )

        if fixture is None:
            raise ValueError(
                f"Quote unavailable for {normalized_symbol}"
            )

        price = Decimal(fixture["price"])
        previous_close = Decimal(
            fixture["previous_close"]
        )

        change = (
            price - previous_close
        ).quantize(
            TWOPLACES,
            rounding=ROUND_HALF_UP,
        )

        change_percent = (
            (change / previous_close) * Decimal("100")
        ).quantize(
            TWOPLACES,
            rounding=ROUND_HALF_UP,
        )

        return MarketQuote(
            symbol=normalized_symbol,
            exchange=exchange,
            currency=Currency.INR,
            price=price,
            previous_close=previous_close,
            change=change,
            change_percent=change_percent,
            open=Decimal(fixture["open"]),
            day_high=Decimal(fixture["day_high"]),
            day_low=Decimal(fixture["day_low"]),
            volume=fixture["volume"],
            as_of=datetime.now(timezone.utc),
            data_status=MarketDataStatus.SIMULATED,
            provider=self.name,
        )