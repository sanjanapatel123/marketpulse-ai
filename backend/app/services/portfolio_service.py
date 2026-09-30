from decimal import Decimal, ROUND_HALF_UP

import asyncio

from app.models.portfolio import PortfolioSummary
from app.services.portfolio_valuation_service import (
    calculate_portfolio_valuation,
)

from fastapi import HTTPException, status

from app.models.enums import (
    Exchange,
    TransactionSide,
)
from app.models.portfolio import (
    CreatePortfolioRequest,
    CreateTradeRequest,
    Portfolio,
    PortfolioTransaction,
    TradeExecutionResponse,
)
from app.repositories.market_repository import find_stock
from app.repositories.portfolio_repository import (
    find_portfolio,
    find_transaction_by_idempotency_key,
    insert_portfolio,
    insert_transaction,
    list_portfolio_transactions,
)
from app.services.market_service import market_provider
from app.services.portfolio_ledger_service import (
    calculate_ledger_state,
)


MONEY_PLACES = Decimal("0.01")
QUANTITY_PLACES = Decimal("0.0001")
FEE_RATE = Decimal("0.001")


def money(value: Decimal) -> Decimal:
    return value.quantize(
        MONEY_PLACES,
        rounding=ROUND_HALF_UP,
    )


def quantity(value: Decimal) -> Decimal:
    return value.quantize(
        QUANTITY_PLACES,
        rounding=ROUND_HALF_UP,
    )


async def create_portfolio(
    payload: CreatePortfolioRequest,
) -> Portfolio:
    portfolio = Portfolio(
        name=payload.name.strip(),
        initial_cash=money(payload.initial_cash),
    )

    return await insert_portfolio(portfolio)


async def get_portfolio_or_404(
    portfolio_id: str,
) -> Portfolio:
    portfolio = await find_portfolio(portfolio_id)

    if portfolio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "PORTFOLIO_NOT_FOUND",
                "message": "Portfolio not found",
            },
        )

    return portfolio


async def execute_trade(
    *,
    portfolio_id: str,
    payload: CreateTradeRequest,
) -> TradeExecutionResponse:
    portfolio = await get_portfolio_or_404(
        portfolio_id
    )

    normalized_symbol = payload.symbol.strip().upper()
    normalized_quantity = quantity(payload.quantity)

    existing_transaction = (
        await find_transaction_by_idempotency_key(
            portfolio_id=portfolio_id,
            idempotency_key=payload.idempotency_key,
        )
    )

    if existing_transaction is not None:
        if (
            existing_transaction.symbol
            != normalized_symbol
            or existing_transaction.side
            != payload.side
            or existing_transaction.quantity
            != normalized_quantity
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "IDEMPOTENCY_CONFLICT",
                    "message": (
                        "Idempotency key was already used "
                        "for a different trade"
                    ),
                },
            )

        transactions = (
            await list_portfolio_transactions(
                portfolio_id
            )
        )

        state = calculate_ledger_state(
            portfolio=portfolio,
            transactions=transactions,
        )

        return TradeExecutionResponse(
            transaction=existing_transaction,
            remaining_cash=state.cash_balance,
            position_quantity=state.quantities.get(
                normalized_symbol,
                Decimal("0"),
            ),
        )

    stock = await find_stock(
        symbol=normalized_symbol,
        exchange=Exchange.NSE.value,
    )

    if stock is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "STOCK_NOT_FOUND",
                "message": (
                    f"Stock {normalized_symbol} "
                    "is not available"
                ),
            },
        )

    existing_transactions = (
        await list_portfolio_transactions(
            portfolio_id
        )
    )

    current_state = calculate_ledger_state(
        portfolio=portfolio,
        transactions=existing_transactions,
    )

    current_position = (
        current_state.quantities.get(
            normalized_symbol,
            Decimal("0"),
        )
    )

    if (
        payload.side == TransactionSide.SELL
        and normalized_quantity > current_position
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "INSUFFICIENT_POSITION",
                "message": (
                    f"Cannot sell {normalized_quantity} "
                    f"shares; current position is "
                    f"{current_position}"
                ),
            },
        )

    quote = await market_provider.get_quote(
        symbol=normalized_symbol,
        exchange=Exchange.NSE,
    )

    executed_price = money(quote.price)

    gross_amount = money(
        executed_price * normalized_quantity
    )

    fees = money(gross_amount * FEE_RATE)

    if payload.side == TransactionSide.BUY:
        net_cash_effect = -(gross_amount + fees)

        if (
            current_state.cash_balance
            + net_cash_effect
            < Decimal("0")
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "INSUFFICIENT_CASH",
                    "message": (
                        "Portfolio does not have enough "
                        "cash for this trade"
                    ),
                },
            )
    else:
        net_cash_effect = gross_amount - fees

    transaction = PortfolioTransaction(
        portfolio_id=portfolio_id,
        idempotency_key=payload.idempotency_key,
        symbol=normalized_symbol,
        exchange=Exchange.NSE,
        side=payload.side,
        quantity=normalized_quantity,
        executed_price=executed_price,
        gross_amount=gross_amount,
        fees=fees,
        net_cash_effect=net_cash_effect,
    )

    stored_transaction = await insert_transaction(
        transaction
    )

    updated_transactions = [
        *existing_transactions,
        stored_transaction,
    ]

    updated_state = calculate_ledger_state(
        portfolio=portfolio,
        transactions=updated_transactions,
    )

    return TradeExecutionResponse(
        transaction=stored_transaction,
        remaining_cash=updated_state.cash_balance,
        position_quantity=(
            updated_state.quantities.get(
                normalized_symbol,
                Decimal("0"),
            )
        ),
    )

async def get_portfolio_summary(
    portfolio_id: str,
) -> PortfolioSummary:
    portfolio = await get_portfolio_or_404(
        portfolio_id
    )

    transactions = (
        await list_portfolio_transactions(
            portfolio_id
        )
    )

    ledger_state = calculate_ledger_state(
        portfolio=portfolio,
        transactions=transactions,
    )

    open_symbols = [
        symbol
        for symbol, held_quantity
        in ledger_state.quantities.items()
        if held_quantity > Decimal("0")
    ]

    async def load_market_price(
        symbol: str,
    ) -> tuple[str, Decimal]:
        quote = await market_provider.get_quote(
            symbol=symbol,
            exchange=Exchange.NSE,
        )

        return symbol, quote.price

    quote_results = await asyncio.gather(
        *[
            load_market_price(symbol)
            for symbol in open_symbols
        ]
    )

    market_prices = dict(quote_results)

    try:
        return calculate_portfolio_valuation(
            portfolio=portfolio,
            transactions=transactions,
            market_prices=market_prices,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "INVALID_PORTFOLIO_LEDGER",
                "message": str(error),
            },
        ) from error