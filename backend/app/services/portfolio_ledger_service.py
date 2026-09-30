from decimal import Decimal

from app.models.enums import TransactionSide
from app.models.portfolio import (
    Portfolio,
    PortfolioLedgerState,
    PortfolioTransaction,
)


def calculate_ledger_state(
    *,
    portfolio: Portfolio,
    transactions: list[PortfolioTransaction],
) -> PortfolioLedgerState:
    cash_balance = portfolio.initial_cash
    quantities: dict[str, Decimal] = {}

    for transaction in sorted(
        transactions,
        key=lambda item: item.executed_at,
    ):
        symbol = transaction.symbol

        current_quantity = quantities.get(
            symbol,
            Decimal("0"),
        )

        cash_balance += transaction.net_cash_effect

        if transaction.side == TransactionSide.BUY:
            quantities[symbol] = (
                current_quantity
                + transaction.quantity
            )
        else:
            quantities[symbol] = (
                current_quantity
                - transaction.quantity
            )

    return PortfolioLedgerState(
        cash_balance=cash_balance,
        quantities=quantities,
    )