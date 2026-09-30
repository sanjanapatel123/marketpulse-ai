from decimal import Decimal
from typing import Any

from bson.decimal128 import Decimal128
from pymongo.errors import DuplicateKeyError

from app.core.database import database
from app.models.portfolio import (
    Portfolio,
    PortfolioTransaction,
)


PORTFOLIO_DECIMAL_FIELDS = {
    "initial_cash",
}

TRANSACTION_DECIMAL_FIELDS = {
    "quantity",
    "executed_price",
    "gross_amount",
    "fees",
    "net_cash_effect",
}


def convert_decimals_to_bson(
    document: dict[str, Any],
    fields: set[str],
) -> dict[str, Any]:
    converted = dict(document)

    for field in fields:
        value = converted.get(field)

        if isinstance(value, Decimal):
            converted[field] = Decimal128(value)

    return converted


def convert_decimals_from_bson(
    document: dict[str, Any],
    fields: set[str],
) -> dict[str, Any]:
    converted = dict(document)
    converted.pop("_id", None)

    for field in fields:
        value = converted.get(field)

        if isinstance(value, Decimal128):
            converted[field] = value.to_decimal()

    return converted


async def insert_portfolio(
    portfolio: Portfolio,
) -> Portfolio:
    document = convert_decimals_to_bson(
        portfolio.model_dump(mode="python"),
        PORTFOLIO_DECIMAL_FIELDS,
    )

    await database.portfolios.insert_one(document)
    return portfolio


async def find_portfolio(
    portfolio_id: str,
) -> Portfolio | None:
    document = await database.portfolios.find_one(
        {
            "id": portfolio_id,
        }
    )

    if document is None:
        return None

    return Portfolio(
        **convert_decimals_from_bson(
            document,
            PORTFOLIO_DECIMAL_FIELDS,
        )
    )


async def list_portfolio_transactions(
    portfolio_id: str,
) -> list[PortfolioTransaction]:
    documents = await database.portfolio_transactions.find(
        {
            "portfolio_id": portfolio_id,
        }
    ).sort(
        "executed_at",
        1,
    ).to_list(length=None)

    return [
        PortfolioTransaction(
            **convert_decimals_from_bson(
                document,
                TRANSACTION_DECIMAL_FIELDS,
            )
        )
        for document in documents
    ]


async def find_transaction_by_idempotency_key(
    *,
    portfolio_id: str,
    idempotency_key: str,
) -> PortfolioTransaction | None:
    document = (
        await database.portfolio_transactions.find_one(
            {
                "portfolio_id": portfolio_id,
                "idempotency_key": idempotency_key,
            }
        )
    )

    if document is None:
        return None

    return PortfolioTransaction(
        **convert_decimals_from_bson(
            document,
            TRANSACTION_DECIMAL_FIELDS,
        )
    )


async def insert_transaction(
    transaction: PortfolioTransaction,
) -> PortfolioTransaction:
    document = convert_decimals_to_bson(
        transaction.model_dump(mode="python"),
        TRANSACTION_DECIMAL_FIELDS,
    )

    try:
        await database.portfolio_transactions.insert_one(
            document
        )
    except DuplicateKeyError:
        existing = (
            await find_transaction_by_idempotency_key(
                portfolio_id=transaction.portfolio_id,
                idempotency_key=(
                    transaction.idempotency_key
                ),
            )
        )

        if existing is None:
            raise

        return existing

    return transaction


async def list_portfolios() -> list[Portfolio]:
    documents = await database.portfolios.find(
        {},
        {
            "_id": 0,
        },
    ).sort(
        "created_at",
        -1,
    ).to_list(length=None)

    return [
        Portfolio(
            **convert_decimals_from_bson(
                document,
                PORTFOLIO_DECIMAL_FIELDS,
            )
        )
        for document in documents
    ]