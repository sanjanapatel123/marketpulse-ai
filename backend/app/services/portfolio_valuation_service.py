from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from app.models.enums import (
    Currency,
    Exchange,
    TransactionSide,
)
from app.models.portfolio import (
    Portfolio,
    PortfolioSummary,
    PortfolioTransaction,
    PositionValuation,
)


MONEY_PLACES = Decimal("0.01")
QUANTITY_PLACES = Decimal("0.0001")
PERCENT_PLACES = Decimal("0.01")
HUNDRED = Decimal("100")


def money(value: Decimal) -> Decimal:
    return value.quantize(
        MONEY_PLACES,
        rounding=ROUND_HALF_UP,
    )


def quantity_value(value: Decimal) -> Decimal:
    return value.quantize(
        QUANTITY_PLACES,
        rounding=ROUND_HALF_UP,
    )


def percentage(value: Decimal) -> Decimal:
    return value.quantize(
        PERCENT_PLACES,
        rounding=ROUND_HALF_UP,
    )


@dataclass
class PositionCostState:
    quantity: Decimal = Decimal("0")
    cost_basis: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")


def calculate_portfolio_valuation(
    *,
    portfolio: Portfolio,
    transactions: list[PortfolioTransaction],
    market_prices: dict[str, Decimal],
) -> PortfolioSummary:
    cash_balance = portfolio.initial_cash
    total_fees = Decimal("0")

    position_states: dict[
        str,
        PositionCostState,
    ] = {}

    for transaction in sorted(
        transactions,
        key=lambda item: item.executed_at,
    ):
        symbol = transaction.symbol

        state = position_states.setdefault(
            symbol,
            PositionCostState(),
        )

        cash_balance += transaction.net_cash_effect
        total_fees += transaction.fees

        if transaction.side == TransactionSide.BUY:
            purchase_cost = (
                transaction.gross_amount
                + transaction.fees
            )

            state.quantity += transaction.quantity
            state.cost_basis += purchase_cost
            continue

        if transaction.quantity > state.quantity:
            raise ValueError(
                f"Transaction ledger oversells {symbol}"
            )

        if state.quantity <= 0:
            raise ValueError(
                f"No open position exists for {symbol}"
            )

        average_cost = (
            state.cost_basis / state.quantity
        )

        sold_cost_basis = (
            average_cost * transaction.quantity
        )

        net_sale_proceeds = (
            transaction.gross_amount
            - transaction.fees
        )

        state.realized_pnl += (
            net_sale_proceeds - sold_cost_basis
        )

        state.quantity -= transaction.quantity
        state.cost_basis -= sold_cost_basis

        if state.quantity == 0:
            state.cost_basis = Decimal("0")

    positions: list[PositionValuation] = []

    total_cost_basis = Decimal("0")
    total_market_value = Decimal("0")
    total_realized_pnl = Decimal("0")
    total_unrealized_pnl = Decimal("0")

    for symbol, state in position_states.items():
        total_realized_pnl += state.realized_pnl

        if state.quantity <= 0:
            continue

        current_price = market_prices.get(symbol)

        if current_price is None:
            raise ValueError(
                f"Market price unavailable for {symbol}"
            )

        average_cost = (
            state.cost_basis / state.quantity
        )

        market_value = (
            state.quantity * current_price
        )

        unrealized_pnl = (
            market_value - state.cost_basis
        )

        unrealized_return = (
            unrealized_pnl
            / state.cost_basis
            * HUNDRED
            if state.cost_basis != 0
            else Decimal("0")
        )

        positions.append(
            PositionValuation(
                symbol=symbol,
                exchange=Exchange.NSE,
                currency=Currency.INR,
                quantity=quantity_value(
                    state.quantity
                ),
                average_cost=money(average_cost),
                cost_basis=money(state.cost_basis),
                current_price=money(
                    current_price
                ),
                market_value=money(market_value),
                unrealized_pnl=money(
                    unrealized_pnl
                ),
                unrealized_return_percent=(
                    percentage(unrealized_return)
                ),
            )
        )

        total_cost_basis += state.cost_basis
        total_market_value += market_value
        total_unrealized_pnl += unrealized_pnl

    positions.sort(
        key=lambda position: position.market_value,
        reverse=True,
    )

    total_pnl = (
        total_realized_pnl
        + total_unrealized_pnl
    )

    total_portfolio_value = (
        cash_balance + total_market_value
    )

    total_return = (
        total_pnl
        / portfolio.initial_cash
        * HUNDRED
    )

    return PortfolioSummary(
        portfolio_id=portfolio.id,
        portfolio_name=portfolio.name,
        currency=portfolio.currency,
        initial_cash=money(
            portfolio.initial_cash
        ),
        cash_balance=money(cash_balance),
        positions_cost_basis=money(
            total_cost_basis
        ),
        positions_market_value=money(
            total_market_value
        ),
        total_portfolio_value=money(
            total_portfolio_value
        ),
        realized_pnl=money(
            total_realized_pnl
        ),
        unrealized_pnl=money(
            total_unrealized_pnl
        ),
        total_pnl=money(total_pnl),
        total_return_percent=percentage(
            total_return
        ),
        total_fees=money(total_fees),
        positions=positions,
    )