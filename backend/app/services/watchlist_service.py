import asyncio

from fastapi import HTTPException, status

from app.models.enums import Exchange
from app.models.watchlist import (
    AddWatchlistItemRequest,
    CreatePriceAlertRequest,
    CreateWatchlistRequest,
    PriceAlert,
    Watchlist,
    WatchlistDetailResponse,
    WatchlistItem,
    WatchlistItemQuote,
)
from app.repositories.market_repository import (
    find_stock,
)
from app.repositories.watchlist_repository import (
    add_watchlist_item,
    find_watchlist,
    insert_price_alert,
    insert_watchlist,
    list_watchlist_alerts,
    list_watchlist_items,
    list_watchlists,
    remove_watchlist_item,
)
from app.services.market_service import market_provider


async def get_watchlist_or_404(
    watchlist_id: str,
) -> Watchlist:
    watchlist = await find_watchlist(watchlist_id)

    if watchlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WATCHLIST_NOT_FOUND",
                "message": "Watchlist not found",
            },
        )

    return watchlist


async def create_watchlist(
    payload: CreateWatchlistRequest,
) -> Watchlist:
    watchlist = Watchlist(
        name=payload.name.strip()
    )

    return await insert_watchlist(watchlist)


async def get_all_watchlists() -> list[Watchlist]:
    return await list_watchlists()


async def add_symbol_to_watchlist(
    *,
    watchlist_id: str,
    payload: AddWatchlistItemRequest,
) -> WatchlistItem:
    await get_watchlist_or_404(watchlist_id)

    symbol = payload.symbol.strip().upper()

    stock = await find_stock(
        symbol=symbol,
        exchange=Exchange.NSE.value,
    )

    if stock is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "STOCK_NOT_FOUND",
                "message": (
                    f"Stock {symbol} is not available"
                ),
            },
        )

    item = WatchlistItem(
        watchlist_id=watchlist_id,
        symbol=symbol,
    )

    return await add_watchlist_item(item)


async def remove_symbol_from_watchlist(
    *,
    watchlist_id: str,
    symbol: str,
) -> None:
    await get_watchlist_or_404(watchlist_id)

    removed = await remove_watchlist_item(
        watchlist_id=watchlist_id,
        symbol=symbol,
    )

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WATCHLIST_ITEM_NOT_FOUND",
                "message": "Stock is not in this watchlist",
            },
        )


async def create_alert(
    *,
    watchlist_id: str,
    payload: CreatePriceAlertRequest,
) -> PriceAlert:
    await get_watchlist_or_404(watchlist_id)

    symbol = payload.symbol.strip().upper()

    items = await list_watchlist_items(
        watchlist_id
    )

    if not any(
        item.symbol == symbol
        for item in items
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "STOCK_NOT_IN_WATCHLIST",
                "message": (
                    "Add the stock to the watchlist "
                    "before creating an alert"
                ),
            },
        )

    alert = PriceAlert(
        watchlist_id=watchlist_id,
        symbol=symbol,
        condition=payload.condition,
        threshold=payload.threshold,
    )

    return await insert_price_alert(alert)


async def get_watchlist_detail(
    watchlist_id: str,
) -> WatchlistDetailResponse:
    watchlist = await get_watchlist_or_404(
        watchlist_id
    )

    items = await list_watchlist_items(
        watchlist_id
    )

    async def enrich_item(
        item: WatchlistItem,
    ) -> WatchlistItemQuote:
        stock = await find_stock(
            symbol=item.symbol,
            exchange=item.exchange.value,
        )

        quote = await market_provider.get_quote(
            symbol=item.symbol,
            exchange=item.exchange,
        )

        return WatchlistItemQuote(
            item=item,
            company_name=stock["company_name"],
            sector=stock["sector"],
            price=quote.price,
            change=quote.change,
            change_percent=quote.change_percent,
            currency=quote.currency,
            data_status=quote.data_status.value,
        )

    enriched_items = await asyncio.gather(
        *[
            enrich_item(item)
            for item in items
        ]
    )

    alerts = await list_watchlist_alerts(
        watchlist_id
    )

    return WatchlistDetailResponse(
        watchlist=watchlist,
        items=enriched_items,
        alerts=alerts,
    )