from decimal import Decimal

from app.models.enums import (
    Exchange,
    TransactionSide,
)
from app.models.portfolio import (
    Portfolio,
    PortfolioTransaction,
)
from app.services.portfolio_valuation_service import (
    calculate_portfolio_valuation,
)


def make_transaction(
    *,
    transaction_id: str,
    side: TransactionSide,
    quantity: str,
    gross_amount: str,
    fees: str,
    cash_effect: str,
) -> PortfolioTransaction:
    return PortfolioTransaction(
        id=transaction_id,
        portfolio_id="portfolio-test",
        idempotency_key=transaction_id,
        symbol="TCS",
        exchange=Exchange.NSE,
        side=side,
        quantity=Decimal(quantity),
        executed_price=Decimal("4215.60"),
        gross_amount=Decimal(gross_amount),
        fees=Decimal(fees),
        net_cash_effect=Decimal(cash_effect),
    )


def create_test_portfolio() -> Portfolio:
    return Portfolio(
        id="portfolio-test",
        name="My Growth Portfolio",
        initial_cash=Decimal("500000"),
    )


def test_same_price_round_trip_loses_fees():
    buy = make_transaction(
        transaction_id="buy-001",
        side=TransactionSide.BUY,
        quantity="10",
        gross_amount="42156.00",
        fees="42.16",
        cash_effect="-42198.16",
    )

    sell = make_transaction(
        transaction_id="sell-001",
        side=TransactionSide.SELL,
        quantity="4",
        gross_amount="16862.40",
        fees="16.86",
        cash_effect="16845.54",
    )

    summary = calculate_portfolio_valuation(
        portfolio=create_test_portfolio(),
        transactions=[buy, sell],
        market_prices={
            "TCS": Decimal("4215.60"),
        },
    )

    assert summary.cash_balance == Decimal(
        "474647.38"
    )

    assert summary.positions[0].quantity == Decimal(
        "6.0000"
    )

    assert summary.positions[0].average_cost == (
        Decimal("4219.82")
    )

    assert summary.realized_pnl == Decimal("-33.72")
    assert summary.unrealized_pnl == Decimal("-25.30")
    assert summary.total_pnl == Decimal("-59.02")
    assert summary.total_fees == Decimal("59.02")

    assert summary.total_portfolio_value == (
        Decimal("499940.98")
    )


def test_profitable_position_calculation():
    buy = make_transaction(
        transaction_id="buy-001",
        side=TransactionSide.BUY,
        quantity="10",
        gross_amount="42156.00",
        fees="42.16",
        cash_effect="-42198.16",
    )

    summary = calculate_portfolio_valuation(
        portfolio=create_test_portfolio(),
        transactions=[buy],
        market_prices={
            "TCS": Decimal("4500.00"),
        },
    )

    position = summary.positions[0]

    assert position.market_value == Decimal(
        "45000.00"
    )

    assert position.unrealized_pnl == Decimal(
        "2801.84"
    )

    assert summary.total_pnl == Decimal(
        "2801.84"
    )


def test_closed_position_has_only_realized_pnl():
    buy = make_transaction(
        transaction_id="buy-001",
        side=TransactionSide.BUY,
        quantity="10",
        gross_amount="42156.00",
        fees="42.16",
        cash_effect="-42198.16",
    )

    sell = make_transaction(
        transaction_id="sell-001",
        side=TransactionSide.SELL,
        quantity="10",
        gross_amount="43000.00",
        fees="43.00",
        cash_effect="42957.00",
    )

    summary = calculate_portfolio_valuation(
        portfolio=create_test_portfolio(),
        transactions=[buy, sell],
        market_prices={},
    )

    assert summary.positions == []
    assert summary.unrealized_pnl == Decimal("0.00")
    assert summary.realized_pnl == Decimal("758.84")
    assert summary.total_pnl == Decimal("758.84")