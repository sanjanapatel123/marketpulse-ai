from decimal import Decimal
from typing import Any
from app.models.market import PriceCandle
from bson.decimal128 import Decimal128

from app.core.database import database
from app.models.market import MarketQuote, Stock


DECIMAL_FIELDS = {
    "price",
    "previous_close",
    "change",
    "change_percent",
    "open",
    "day_high",
    "day_low",
}

CANDLE_DECIMAL_FIELDS = {
    "open",
    "high",
    "low",
    "close",
    "previous_close",
    "return_percent",
}


def quote_to_document(
    quote: MarketQuote,
) -> dict[str, Any]:
    document = quote.model_dump(mode="python")

    for field in DECIMAL_FIELDS:
        value = document[field]

        if isinstance(value, Decimal):
            document[field] = Decimal128(value)

    return document


def decimal128_to_string(
    value: Decimal128,
) -> str:
    return str(value.to_decimal())


async def save_quote(
    quote: MarketQuote,
) -> None:
    document = quote_to_document(quote)
    await database.market_quotes.insert_one(document)


async def find_stock(
    *,
    symbol: str,
    exchange: str = "NSE",
) -> dict | None:
    return await database.stocks.find_one(
        {
            "symbol": symbol.upper(),
            "exchange": exchange,
            "is_active": True,
        },
        {
            "_id": 0,
        },
    )


async def list_stocks() -> list[dict]:
    return await database.stocks.find(
        {
            "is_active": True,
        },
        {
            "_id": 0,
        },
    ).sort("symbol", 1).to_list(length=None)


async def upsert_stock(stock: Stock) -> None:
    document = stock.model_dump(mode="python")

    await database.stocks.update_one(
        {
            "symbol": stock.symbol,
            "exchange": stock.exchange.value,
        },
        {
            "$setOnInsert": document,
        },
        upsert=True,
    )

def candle_to_document(
    candle: PriceCandle,
) -> dict[str, Any]:
    document = candle.model_dump(mode="python")

    metadata = {
        "symbol": document.pop("symbol"),
        "exchange": document.pop("exchange"),
        "currency": document.pop("currency"),
        "interval": document.pop("interval"),
        "provider": document.pop("provider"),
        "data_status": document.pop("data_status"),
    }

    document["metadata"] = metadata

    for field in CANDLE_DECIMAL_FIELDS:
        value = document.get(field)

        if isinstance(value, Decimal):
            document[field] = Decimal128(value)

    return document


def candle_from_document(
    document: dict[str, Any],
) -> PriceCandle:
    metadata = document["metadata"]

    converted = {
        "id": document["id"],
        "symbol": metadata["symbol"],
        "exchange": metadata["exchange"],
        "currency": metadata["currency"],
        "interval": metadata["interval"],
        "provider": metadata["provider"],
        "data_status": metadata["data_status"],
        "timestamp": document["timestamp"],
        "volume": document["volume"],
    }

    for field in CANDLE_DECIMAL_FIELDS:
        value = document.get(field)

        if isinstance(value, Decimal128):
            converted[field] = value.to_decimal()
        else:
            converted[field] = value

    return PriceCandle(**converted)


async def save_missing_candles(
    candles: list[PriceCandle],
) -> int:
    if not candles:
        return 0

    symbol = candles[0].symbol

    existing_documents = await (
        database.price_candles.find(
            {
                "metadata.symbol": symbol,
                "metadata.interval": "1d",
            },
            {
                "_id": 0,
                "id": 1,
            },
        ).to_list(length=None)
    )

    existing_ids = {
        document["id"]
        for document in existing_documents
    }

    documents_to_insert = [
        candle_to_document(candle)
        for candle in candles
        if candle.id not in existing_ids
    ]

    if not documents_to_insert:
        return 0

    result = await database.price_candles.insert_many(
        documents_to_insert
    )

    return len(result.inserted_ids)


async def get_price_history(
    *,
    symbol: str,
    days: int,
) -> list[PriceCandle]:
    documents = await database.price_candles.find(
        {
            "metadata.symbol": symbol.upper(),
            "metadata.exchange": "NSE",
            "metadata.interval": "1d",
        },
        {
            "_id": 0,
        },
    ).sort(
        "timestamp",
        -1,
    ).limit(days).to_list(length=days)

    documents.reverse()

    return [
        candle_from_document(document)
        for document in documents
    ]