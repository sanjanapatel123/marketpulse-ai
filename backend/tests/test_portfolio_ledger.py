from decimal import Decimal

from app.models.enums import (
    Exchange,
    TransactionSide,
)
from app.models.portfolio import (
    Portfolio,
    PortfolioTransaction,
)
from app.services.portfolio_ledger_service import (
    calculate_ledger_state,
)


def make_transaction(
    *,
    side: TransactionSide,
    quantity: str,
    cash_effect: str,
) -> PortfolioTransaction:
    return PortfolioTransaction(
        portfolio_id="portfolio-test",
        idempotency_key=f"trade-{side}-{quantity}",
        symbol="TCS",
        exchange=Exchange.NSE,
        side=side,
        quantity=Decimal(quantity),
        executed_price=Decimal("4000"),
        gross_amount=Decimal("40000"),
        fees=Decimal("40"),
        net_cash_effect=Decimal(cash_effect),
    )


def test_buy_reduces_cash_and_adds_position():
    portfolio = Portfolio(
        name="Test Portfolio",
        initial_cash=Decimal("100000"),
    )

    transaction = make_transaction(
        side=TransactionSide.BUY,
        quantity="10",
        cash_effect="-40040",
    )

    state = calculate_ledger_state(
        portfolio=portfolio,
        transactions=[transaction],
    )

    assert state.cash_balance == Decimal("59960")
    assert state.quantities["TCS"] == Decimal("10")


def test_sell_increases_cash_and_reduces_position():
    portfolio = Portfolio(
        name="Test Portfolio",
        initial_cash=Decimal("100000"),
    )

    buy = make_transaction(
        side=TransactionSide.BUY,
        quantity="10",
        cash_effect="-40040",
    )

    sell = make_transaction(
        side=TransactionSide.SELL,
        quantity="4",
        cash_effect="15984",
    )

    state = calculate_ledger_state(
        portfolio=portfolio,
        transactions=[buy, sell],
    )

    assert state.cash_balance == Decimal("75944")
    assert state.quantities["TCS"] == Decimal("6")


def test_ledger_calculation_is_deterministic():
    portfolio = Portfolio(
        name="Test Portfolio",
        initial_cash=Decimal("100000"),
    )

    transactions = [
        make_transaction(
            side=TransactionSide.BUY,
            quantity="10",
            cash_effect="-40040",
        )
    ]

    first = calculate_ledger_state(
        portfolio=portfolio,
        transactions=transactions,
    )

    second = calculate_ledger_state(
        portfolio=portfolio,
        transactions=transactions,
    )

    assert first == second