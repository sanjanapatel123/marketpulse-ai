from decimal import Decimal

from app.providers.deterministic_fundamentals import (
    generate_financial_statements,
)
from app.services.fundamental_ratio_service import (
    calculate_fundamental_ratios,
)


def test_fundamental_ratio_calculation():
    statements = generate_financial_statements(
        "TCS"
    )

    previous = statements[0]
    latest = statements[1]

    ratios = calculate_fundamental_ratios(
        latest=latest,
        previous=previous,
        market_price=Decimal("4215.60"),
    )

    assert ratios.earnings_per_share > 0
    assert ratios.price_to_earnings > 0
    assert ratios.return_on_equity_percent > 0
    assert ratios.revenue_growth_percent is not None
    assert ratios.current_ratio > 0


def test_revenue_growth_formula():
    statements = generate_financial_statements(
        "INFY"
    )

    ratios = calculate_fundamental_ratios(
        latest=statements[1],
        previous=statements[0],
        market_price=Decimal("1824.75"),
    )

    expected_growth = (
        (
            statements[1].revenue
            - statements[0].revenue
        )
        / statements[0].revenue
        * Decimal("100")
    ).quantize(Decimal("0.01"))

    assert (
        ratios.revenue_growth_percent
        == expected_growth
    )


def test_ratios_are_deterministic():
    statements = generate_financial_statements(
        "RELIANCE"
    )

    first = calculate_fundamental_ratios(
        latest=statements[1],
        previous=statements[0],
        market_price=Decimal("2984.35"),
    )

    second = calculate_fundamental_ratios(
        latest=statements[1],
        previous=statements[0],
        market_price=Decimal("2984.35"),
    )

    assert first == second