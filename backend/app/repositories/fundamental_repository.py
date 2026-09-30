from decimal import Decimal
from typing import Any

from bson.decimal128 import Decimal128

from app.core.database import database
from app.models.market import FinancialStatement


DECIMAL_FIELDS = {
    "revenue",
    "ebitda",
    "ebit",
    "net_income",
    "total_assets",
    "shareholder_equity",
    "total_debt",
    "current_assets",
    "current_liabilities",
    "shares_outstanding",
}


def statement_to_document(
    statement: FinancialStatement,
) -> dict[str, Any]:
    document = statement.model_dump(mode="python")

    for field in DECIMAL_FIELDS:
        value = document[field]

        if isinstance(value, Decimal):
            document[field] = Decimal128(value)

    return document


def statement_from_document(
    document: dict[str, Any],
) -> FinancialStatement:
    converted = dict(document)
    converted.pop("_id", None)

    for field in DECIMAL_FIELDS:
        value = converted[field]

        if isinstance(value, Decimal128):
            converted[field] = value.to_decimal()

    return FinancialStatement(**converted)


async def save_financial_statements(
    statements: list[FinancialStatement],
) -> int:
    saved_count = 0

    for statement in statements:
        result = (
            await database.financial_statements.update_one(
                {
                    "symbol": statement.symbol,
                    "fiscal_year": (
                        statement.fiscal_year
                    ),
                },
                {
                    "$setOnInsert": (
                        statement_to_document(statement)
                    )
                },
                upsert=True,
            )
        )

        if result.upserted_id is not None:
            saved_count += 1

    return saved_count


async def get_financial_statements(
    symbol: str,
) -> list[FinancialStatement]:
    documents = await (
        database.financial_statements.find(
            {
                "symbol": symbol.upper(),
            }
        )
        .sort("fiscal_year", -1)
        .limit(2)
        .to_list(length=2)
    )

    return [
        statement_from_document(document)
        for document in documents
    ]