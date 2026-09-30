from fastapi import HTTPException, status
from decimal import Decimal
from app.models.enums import Exchange
from app.models.market import (MarketQuote , FundamentalsResponse)
from app.providers.base import MarketDataProvider
from app.providers.deterministic_market import (
    DeterministicMarketDataProvider,
)
from app.repositories.market_repository import (
    find_stock,
    list_stocks,
    save_quote,
)

from app.models.market import (
    MarketQuote,
    PriceHistoryResponse,
)
from app.repositories.market_repository import (
    find_stock,
    get_price_history,
    list_stocks,
    save_quote,
)
from app.repositories.fundamental_repository import (
    get_financial_statements,
)
from app.services.fundamental_ratio_service import (
    calculate_fundamental_ratios,
)



market_provider: MarketDataProvider = (
    DeterministicMarketDataProvider()
)


async def get_available_stocks() -> list[dict]:
    return await list_stocks()


async def get_latest_quote(
    symbol: str,
) -> MarketQuote:
    normalized_symbol = symbol.strip().upper()

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

    try:
        quote = await market_provider.get_quote(
            symbol=normalized_symbol,
            exchange=Exchange.NSE,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "QUOTE_UNAVAILABLE",
                "message": str(error),
            },
        ) from error

    await save_quote(quote)

    return quote

async def get_historical_prices(
    *,
    symbol: str,
    days: int,
) -> PriceHistoryResponse:
    normalized_symbol = symbol.strip().upper()

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

    candles = await get_price_history(
        symbol=normalized_symbol,
        days=days,
    )

    if not candles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "HISTORY_NOT_FOUND",
                "message": (
                    "Historical price data is unavailable"
                ),
            },
        )

    return PriceHistoryResponse(
    symbol=normalized_symbol,
    exchange=Exchange.NSE,
    currency=stock["currency"],
    interval="1d",
    provider=candles[0].provider,
    data_status=candles[0].data_status,
    count=len(candles),
    candles=candles,
)

async def get_company_fundamentals(
    symbol: str,
) -> FundamentalsResponse:
    normalized_symbol = symbol.strip().upper()

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

    statements = await get_financial_statements(
        normalized_symbol
    )

    if not statements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "FUNDAMENTALS_NOT_FOUND",
                "message": (
                    "Financial statements unavailable"
                ),
            },
        )

    latest = statements[0]

    previous = (
        statements[1]
        if len(statements) > 1
        else None
    )

    quote = await market_provider.get_quote(
        symbol=normalized_symbol,
        exchange=Exchange.NSE,
    )

    ratios = calculate_fundamental_ratios(
        latest=latest,
        previous=previous,
        market_price=Decimal(quote.price),
    )

    return FundamentalsResponse(
        symbol=normalized_symbol,
        exchange=Exchange.NSE,
        data_status=latest.data_status,
        provider=latest.provider,
        latest_statement=latest,
        previous_statement=previous,
        ratios=ratios,
    )