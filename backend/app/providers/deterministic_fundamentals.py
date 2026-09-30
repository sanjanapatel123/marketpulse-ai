from datetime import datetime, timezone
from decimal import Decimal
from uuid import NAMESPACE_URL, uuid5

from app.models.enums import (
    Currency,
    Exchange,
    MarketDataStatus,
)
from app.models.market import FinancialStatement


FUNDAMENTAL_FIXTURES = {
    "RELIANCE": [
        {
            "fiscal_year": "FY2025",
            "revenue": "964693",
            "ebitda": "178677",
            "ebit": "129432",
            "net_income": "79020",
            "total_assets": "1863220",
            "shareholder_equity": "987000",
            "total_debt": "346500",
            "current_assets": "412000",
            "current_liabilities": "398000",
            "shares_outstanding": "676.60",
        },
        {
            "fiscal_year": "FY2026",
            "revenue": "1015000",
            "ebitda": "192000",
            "ebit": "141500",
            "net_income": "85200",
            "total_assets": "1925000",
            "shareholder_equity": "1045000",
            "total_debt": "332000",
            "current_assets": "438000",
            "current_liabilities": "405000",
            "shares_outstanding": "676.60",
        },
    ],
    "TCS": [
        {
            "fiscal_year": "FY2025",
            "revenue": "255324",
            "ebitda": "67500",
            "ebit": "64500",
            "net_income": "48200",
            "total_assets": "151000",
            "shareholder_equity": "91000",
            "total_debt": "8200",
            "current_assets": "89000",
            "current_liabilities": "42000",
            "shares_outstanding": "362.00",
        },
        {
            "fiscal_year": "FY2026",
            "revenue": "276000",
            "ebitda": "74200",
            "ebit": "70800",
            "net_income": "52600",
            "total_assets": "162000",
            "shareholder_equity": "98500",
            "total_debt": "7600",
            "current_assets": "96200",
            "current_liabilities": "44800",
            "shares_outstanding": "362.00",
        },
    ],
    "INFY": [
        {
            "fiscal_year": "FY2025",
            "revenue": "162990",
            "ebitda": "39700",
            "ebit": "36500",
            "net_income": "26750",
            "total_assets": "137000",
            "shareholder_equity": "86000",
            "total_debt": "7300",
            "current_assets": "79000",
            "current_liabilities": "41000",
            "shares_outstanding": "414.80",
        },
        {
            "fiscal_year": "FY2026",
            "revenue": "176500",
            "ebitda": "43100",
            "ebit": "39800",
            "net_income": "29100",
            "total_assets": "145500",
            "shareholder_equity": "91400",
            "total_debt": "6900",
            "current_assets": "84600",
            "current_liabilities": "42800",
            "shares_outstanding": "414.80",
        },
    ],
}


def generate_financial_statements(
    symbol: str,
) -> list[FinancialStatement]:
    normalized_symbol = symbol.strip().upper()
    fixtures = FUNDAMENTAL_FIXTURES.get(
        normalized_symbol
    )

    if fixtures is None:
        raise ValueError(
            f"Fundamentals unavailable for "
            f"{normalized_symbol}"
        )

    statements: list[FinancialStatement] = []

    for fixture in fixtures:
        statement_id = str(
            uuid5(
                NAMESPACE_URL,
                (
                    f"marketpulse:{normalized_symbol}:"
                    f"{fixture['fiscal_year']}"
                ),
            )
        )

        statements.append(
            FinancialStatement(
                id=statement_id,
                symbol=normalized_symbol,
                exchange=Exchange.NSE,
                fiscal_year=fixture["fiscal_year"],
                currency=Currency.INR,
                revenue=Decimal(fixture["revenue"]),
                ebitda=Decimal(fixture["ebitda"]),
                ebit=Decimal(fixture["ebit"]),
                net_income=Decimal(
                    fixture["net_income"]
                ),
                total_assets=Decimal(
                    fixture["total_assets"]
                ),
                shareholder_equity=Decimal(
                    fixture["shareholder_equity"]
                ),
                total_debt=Decimal(
                    fixture["total_debt"]
                ),
                current_assets=Decimal(
                    fixture["current_assets"]
                ),
                current_liabilities=Decimal(
                    fixture["current_liabilities"]
                ),
                shares_outstanding=Decimal(
                    fixture["shares_outstanding"]
                ),
                data_status=(
                    MarketDataStatus.SIMULATED
                ),
                provider=(
                    "deterministic-fundamentals-provider"
                ),
                reported_at=datetime(
                    int(
                        fixture["fiscal_year"].replace(
                            "FY",
                            "",
                        )
                    ),
                    3,
                    31,
                    tzinfo=timezone.utc,
                ),
            )
        )

    return statements