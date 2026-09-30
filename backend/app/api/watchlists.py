from fastapi import APIRouter, Response, status

from app.models.watchlist import (
    AddWatchlistItemRequest,
    AlertEvaluationResult,
    CreatePriceAlertRequest,
    CreateWatchlistRequest,
    PriceAlert,
    Watchlist,
    WatchlistDetailResponse,
    WatchlistItem,
)

from app.services.price_alert_service import evaluate_price_alerts

from app.services.watchlist_service import (
    add_symbol_to_watchlist,
    create_alert,
    create_watchlist,
    get_all_watchlists,
    get_watchlist_detail,
    remove_symbol_from_watchlist,
)


router = APIRouter(
    prefix="/api/watchlists",
    tags=["Watchlists"],
)


# ---------------------------------------------------------
# Watchlist collection routes
# ---------------------------------------------------------

@router.post(
    "",
    response_model=Watchlist,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_watchlist(
    payload: CreateWatchlistRequest,
) -> Watchlist:
    return await create_watchlist(payload)


@router.get("")
async def get_watchlists() -> dict:
    watchlists = await get_all_watchlists()

    return {
        "data": watchlists,
        "count": len(watchlists),
    }


# ---------------------------------------------------------
# Alert evaluation
# Important: Keep this before /{watchlist_id}
# ---------------------------------------------------------

@router.post(
    "/alerts/evaluate",
    response_model=AlertEvaluationResult,
    status_code=status.HTTP_200_OK,
)
async def evaluate_alerts() -> AlertEvaluationResult:
    return await evaluate_price_alerts()


# ---------------------------------------------------------
# Single watchlist routes
# ---------------------------------------------------------

@router.get(
    "/{watchlist_id}",
    response_model=WatchlistDetailResponse,
)
async def get_watchlist(
    watchlist_id: str,
) -> WatchlistDetailResponse:
    return await get_watchlist_detail(watchlist_id)


# ---------------------------------------------------------
# Watchlist item routes
# ---------------------------------------------------------

@router.post(
    "/{watchlist_id}/items",
    response_model=WatchlistItem,
    status_code=status.HTTP_201_CREATED,
)
async def add_item(
    watchlist_id: str,
    payload: AddWatchlistItemRequest,
) -> WatchlistItem:
    return await add_symbol_to_watchlist(
        watchlist_id=watchlist_id,
        payload=payload,
    )


@router.delete(
    "/{watchlist_id}/items/{symbol}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_item(
    watchlist_id: str,
    symbol: str,
) -> Response:
    await remove_symbol_from_watchlist(
        watchlist_id=watchlist_id,
        symbol=symbol,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


# ---------------------------------------------------------
# Price alert routes
# ---------------------------------------------------------

@router.post(
    "/{watchlist_id}/alerts",
    response_model=PriceAlert,
    status_code=status.HTTP_201_CREATED,
)
async def add_alert(
    watchlist_id: str,
    payload: CreatePriceAlertRequest,
) -> PriceAlert:
    return await create_alert(
        watchlist_id=watchlist_id,
        payload=payload,
    )