from decimal import Decimal

import pytest

from app.models.enums import (
    Exchange,
    MarketDataStatus,
)
from app.providers.deterministic_market import (
    DeterministicMarketDataProvider,
)


@pytest.mark.asyncio
async def test_quote_calculation_is_correct():
    provider = DeterministicMarketDataProvider()

    quote = await provider.get_quote(
        symbol="RELIANCE",
        exchange=Exchange.NSE,
    )

    assert quote.price == Decimal("2984.35")
    assert quote.previous_close == Decimal("2950.10")
    assert quote.change == Decimal("34.25")
    assert quote.change_percent == Decimal("1.16")
    assert quote.data_status == (
        MarketDataStatus.SIMULATED
    )


@pytest.mark.asyncio
async def test_provider_is_financially_deterministic():
    provider = DeterministicMarketDataProvider()

    first = await provider.get_quote(
        symbol="TCS",
        exchange=Exchange.NSE,
    )

    second = await provider.get_quote(
        symbol="TCS",
        exchange=Exchange.NSE,
    )

    assert first.price == second.price
    assert first.change == second.change
    assert (
        first.change_percent
        == second.change_percent
    )


@pytest.mark.asyncio
async def test_unknown_symbol_is_rejected():
    provider = DeterministicMarketDataProvider()

    with pytest.raises(
        ValueError,
        match="Quote unavailable",
    ):
        await provider.get_quote(
            symbol="UNKNOWN",
            exchange=Exchange.NSE,
        )