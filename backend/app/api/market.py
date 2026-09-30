from fastapi import APIRouter, Query

from app.models.market import (
    MarketQuote,
    PriceHistoryResponse,
    FundamentalsResponse
)
from app.services.market_service import (
    get_available_stocks,
    get_historical_prices,
    get_latest_quote,
    get_company_fundamentals
)

router = APIRouter(
    prefix="/api/market",
    tags=["Market Data"],
)


@router.get("/stocks")
async def get_stocks():
    stocks = await get_available_stocks()

    return {
        "data": stocks,
        "count": len(stocks),
    }


@router.get(
    "/quotes/{symbol}",
    response_model=MarketQuote,
)
async def get_quote(
    symbol: str,
) -> MarketQuote:
    return await get_latest_quote(symbol)


@router.get(
    "/stocks/{symbol}/history",
    response_model=PriceHistoryResponse,
)
async def get_stock_history(
    symbol: str,
    days: int = Query(
        default=30,
        ge=5,
        le=90,
    ),
) -> PriceHistoryResponse:
    return await get_historical_prices(
        symbol=symbol,
        days=days,
    )

@router.get(
    "/stocks/{symbol}/fundamentals",
    response_model=FundamentalsResponse,
)
async def get_stock_fundamentals(
    symbol: str,
) -> FundamentalsResponse:
    return await get_company_fundamentals(symbol)