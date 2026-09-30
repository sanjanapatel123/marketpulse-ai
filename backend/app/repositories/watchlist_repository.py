from decimal import Decimal
from bson.decimal128 import Decimal128
from typing import Any
from datetime import datetime

from app.models.enums import PriceAlertStatus

from bson.decimal128 import Decimal128
from pymongo import ( ReturnDocument , ASCENDING )

from app.core.database import database
from app.models.watchlist import (
    PriceAlert,
    Watchlist,
    WatchlistItem,
)


ALERT_DECIMAL_FIELDS = {
    "threshold",
    "triggered_price",
}

def _deserialize_price_alert(
    document: dict,
) -> PriceAlert:
    data = document.copy()
    data.pop("_id", None)

    threshold = data.get("threshold")

    if isinstance(threshold, Decimal128):
        data["threshold"] = threshold.to_decimal()

    triggered_price = data.get(
        "triggered_price"
    )

    if isinstance(triggered_price, Decimal128):
        data["triggered_price"] = (
            triggered_price.to_decimal()
        )

    return PriceAlert.model_validate(data)


def alert_to_document(
    alert: PriceAlert,
) -> dict[str, Any]:
    document = alert.model_dump(mode="python")

    for field in ALERT_DECIMAL_FIELDS:
        value = document.get(field)

        if isinstance(value, Decimal):
            document[field] = Decimal128(value)

    return document


def alert_from_document(
    document: dict[str, Any],
) -> PriceAlert:
    converted = dict(document)
    converted.pop("_id", None)

    for field in ALERT_DECIMAL_FIELDS:
        value = converted.get(field)

        if isinstance(value, Decimal128):
            converted[field] = value.to_decimal()

    return PriceAlert(**converted)


async def insert_watchlist(
    watchlist: Watchlist,
) -> Watchlist:
    await database.watchlists.insert_one(
        watchlist.model_dump(mode="python")
    )

    return watchlist


async def list_watchlists() -> list[Watchlist]:
    documents = await database.watchlists.find(
        {},
        {"_id": 0},
    ).sort("created_at", -1).to_list(length=None)

    return [
        Watchlist(**document)
        for document in documents
    ]


async def find_watchlist(
    watchlist_id: str,
) -> Watchlist | None:
    document = await database.watchlists.find_one(
        {"id": watchlist_id},
        {"_id": 0},
    )

    return (
        Watchlist(**document)
        if document is not None
        else None
    )


async def add_watchlist_item(
    item: WatchlistItem,
) -> WatchlistItem:
    document = await (
        database.watchlist_items.find_one_and_update(
            {
                "watchlist_id": item.watchlist_id,
                "symbol": item.symbol,
                "exchange": item.exchange.value,
            },
            {
                "$setOnInsert": item.model_dump(
                    mode="python"
                )
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
            projection={"_id": 0},
        )
    )

    return WatchlistItem(**document)


async def list_watchlist_items(
    watchlist_id: str,
) -> list[WatchlistItem]:
    documents = await database.watchlist_items.find(
        {"watchlist_id": watchlist_id},
        {"_id": 0},
    ).sort("added_at", 1).to_list(length=None)

    return [
        WatchlistItem(**document)
        for document in documents
    ]


async def remove_watchlist_item(
    *,
    watchlist_id: str,
    symbol: str,
) -> bool:
    result = await database.watchlist_items.delete_one(
        {
            "watchlist_id": watchlist_id,
            "symbol": symbol.upper(),
        }
    )

    return result.deleted_count == 1


async def insert_price_alert(
    alert: PriceAlert,
) -> PriceAlert:
    await database.price_alerts.insert_one(
        alert_to_document(alert)
    )

    return alert


async def list_watchlist_alerts(
    watchlist_id: str,
) -> list[PriceAlert]:
    documents = await database.price_alerts.find(
        {"watchlist_id": watchlist_id}
    ).sort("created_at", -1).to_list(length=None)

    return [
        alert_from_document(document)
        for document in documents
    ]

async def list_active_alerts() -> list[PriceAlert]:
    documents = await database.price_alerts.find(
        {
            "status": PriceAlertStatus.ACTIVE.value,
        }
    ).sort(
        "created_at",
        1,
    ).to_list(length=None)

    return [
        alert_from_document(document)
        for document in documents
    ]


async def mark_alert_triggered(
    *,
    alert_id: str,
    triggered_price: Decimal,
    triggered_at: datetime,
) -> PriceAlert | None:
    document = await (
        database.price_alerts.find_one_and_update(
            {
                "id": alert_id,
                "status": (
                    PriceAlertStatus.ACTIVE.value
                ),
            },
            {
                "$set": {
                    "status": (
                        PriceAlertStatus.TRIGGERED.value
                    ),
                    "triggered_price": Decimal128(
                        triggered_price
                    ),
                    "triggered_at": triggered_at,
                    "updated_at": triggered_at,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
    )

    if document is None:
        return None

    return alert_from_document(document)

async def list_triggered_price_alerts(
    limit: int = 500,
) -> list[PriceAlert]:
    safe_limit = max(
        1,
        min(limit, 1000),
    )

    documents = (
        await database.price_alerts.find(
            {
                "status": "TRIGGERED",
            }
        )
        .sort(
            "triggered_at",
            ASCENDING,
        )
        .limit(safe_limit)
        .to_list(length=safe_limit)
    )

    return [
        _deserialize_price_alert(document)
        for document in documents
    ]