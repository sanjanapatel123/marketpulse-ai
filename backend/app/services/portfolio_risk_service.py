from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status

from app.models.portfolio import (
    PortfolioRiskMetrics,
)
from app.repositories.market_repository import (
    get_price_history,
)
from app.services.portfolio_service import (
    get_portfolio_summary,
)
from app.services.portfolio_risk_engine import (
    calculate_portfolio_risk,
)


async def get_portfolio_risk(
    portfolio_id: str,
) -> PortfolioRiskMetrics:
    summary = await get_portfolio_summary(
        portfolio_id
    )

    position_values = {
        position.symbol: position.market_value
        for position in summary.positions
    }

    if not position_values:
        return calculate_portfolio_risk(
            portfolio_id=portfolio_id,
            position_values={},
            returns_by_symbol={},
        )

    returns_by_symbol: dict[
        str,
        dict[date, Decimal],
    ] = {}

    for symbol in position_values:
        candles = await get_price_history(
            symbol=symbol,
            days=90,
        )

        returns_by_symbol[symbol] = {
            candle.timestamp.date(): (
                candle.return_percent
                / Decimal("100")
            )
            for candle in candles
            if candle.return_percent is not None
        }

    try:
        return calculate_portfolio_risk(
            portfolio_id=portfolio_id,
            position_values=position_values,
            returns_by_symbol=returns_by_symbol,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "RISK_CALCULATION_UNAVAILABLE",
                "message": str(error),
            },
        ) from error