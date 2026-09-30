from decimal import Decimal, ROUND_HALF_UP

from app.models.market import (
    FinancialStatement,
    FundamentalRatios,
)


TWO_PLACES = Decimal("0.01")
HUNDRED = Decimal("100")


def rounded(value: Decimal) -> Decimal:
    return value.quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP,
    )


def safe_divide(
    numerator: Decimal,
    denominator: Decimal,
) -> Decimal:
    if denominator == 0:
        raise ValueError(
            "Financial ratio denominator cannot be zero"
        )

    return numerator / denominator


def calculate_fundamental_ratios(
    *,
    latest: FinancialStatement,
    previous: FinancialStatement | None,
    market_price: Decimal,
) -> FundamentalRatios:
    earnings_per_share = safe_divide(
        latest.net_income,
        latest.shares_outstanding,
    )

    book_value_per_share = safe_divide(
        latest.shareholder_equity,
        latest.shares_outstanding,
    )

    price_to_earnings = safe_divide(
        market_price,
        earnings_per_share,
    )

    price_to_book = safe_divide(
        market_price,
        book_value_per_share,
    )

    return_on_equity = (
        safe_divide(
            latest.net_income,
            latest.shareholder_equity,
        )
        * HUNDRED
    )

    capital_employed = (
        latest.total_assets
        - latest.current_liabilities
    )

    return_on_capital_employed = (
        safe_divide(
            latest.ebit,
            capital_employed,
        )
        * HUNDRED
    )

    net_profit_margin = (
        safe_divide(
            latest.net_income,
            latest.revenue,
        )
        * HUNDRED
    )

    debt_to_equity = safe_divide(
        latest.total_debt,
        latest.shareholder_equity,
    )

    current_ratio = safe_divide(
        latest.current_assets,
        latest.current_liabilities,
    )

    revenue_growth: Decimal | None = None

    if previous is not None:
        revenue_growth = (
            safe_divide(
                latest.revenue - previous.revenue,
                previous.revenue,
            )
            * HUNDRED
        )

    return FundamentalRatios(
        symbol=latest.symbol,
        fiscal_year=latest.fiscal_year,
        currency=latest.currency,
        earnings_per_share=rounded(
            earnings_per_share
        ),
        book_value_per_share=rounded(
            book_value_per_share
        ),
        price_to_earnings=rounded(
            price_to_earnings
        ),
        price_to_book=rounded(price_to_book),
        return_on_equity_percent=rounded(
            return_on_equity
        ),
        return_on_capital_employed_percent=(
            rounded(return_on_capital_employed)
        ),
        net_profit_margin_percent=rounded(
            net_profit_margin
        ),
        revenue_growth_percent=(
            rounded(revenue_growth)
            if revenue_growth is not None
            else None
        ),
        debt_to_equity=rounded(debt_to_equity),
        current_ratio=rounded(current_ratio),
    )