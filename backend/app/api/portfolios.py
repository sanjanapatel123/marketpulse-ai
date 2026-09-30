from fastapi import APIRouter, status

from app.models.portfolio import (
    CreatePortfolioRequest,
    CreateTradeRequest,
    Portfolio,
    PortfolioRiskMetrics,
    PortfolioSummary,
    TradeExecutionResponse,
)

from app.services.portfolio_risk_service import (
    get_portfolio_risk,
)
from app.repositories.portfolio_repository import (
    list_portfolios,
    list_portfolio_transactions,
)
from app.services.portfolio_service import (
    create_portfolio,
    execute_trade,
    get_portfolio_or_404,
    get_portfolio_summary,
)

router = APIRouter(
    prefix="/api/portfolios",
    tags=["Paper Portfolios"],
)


@router.post(
    "",
    response_model=Portfolio,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_portfolio(
    payload: CreatePortfolioRequest,
) -> Portfolio:
    return await create_portfolio(payload)


@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: str):
    portfolio = await get_portfolio_or_404(
        portfolio_id
    )

    transactions = (
        await list_portfolio_transactions(
            portfolio_id
        )
    )

    return {
        "portfolio": portfolio,
        "transactions": transactions,
    }


@router.post(
    "/{portfolio_id}/trades",
    response_model=TradeExecutionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_trade(
    portfolio_id: str,
    payload: CreateTradeRequest,
) -> TradeExecutionResponse:
    return await execute_trade(
        portfolio_id=portfolio_id,
        payload=payload,
    )

@router.get("")
async def get_portfolios():
    portfolios = await list_portfolios()

    return {
        "data": portfolios,
        "count": len(portfolios),
    }

@router.get(
    "/{portfolio_id}/summary",
    response_model=PortfolioSummary,
)
async def get_summary(
    portfolio_id: str,
) -> PortfolioSummary:
    return await get_portfolio_summary(
        portfolio_id
    )

@router.get(
    "/{portfolio_id}/risk",
    response_model=PortfolioRiskMetrics,
)
async def get_risk_metrics(
    portfolio_id: str,
) -> PortfolioRiskMetrics:
    return await get_portfolio_risk(
        portfolio_id
    )