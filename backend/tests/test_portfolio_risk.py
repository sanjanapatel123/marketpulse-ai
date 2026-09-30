from datetime import date, timedelta
from decimal import Decimal

from app.services.portfolio_risk_engine import (
    calculate_portfolio_risk,
)


def build_returns(
    values: list[str],
) -> dict[date, Decimal]:
    start = date(2026, 1, 1)

    return {
        start + timedelta(days=index): Decimal(
            value
        )
        for index, value in enumerate(values)
    }


def test_risk_metrics_are_calculated():
    returns = build_returns(
        [
            "0.01",
            "-0.02",
            "0.015",
            "-0.005",
            "0.008",
            "-0.012",
            "0.006",
        ]
    )

    metrics = calculate_portfolio_risk(
        portfolio_id="portfolio-test",
        position_values={
            "TCS": Decimal("100000"),
        },
        returns_by_symbol={
            "TCS": returns,
        },
    )

    assert metrics.observation_count == 7
    assert (
        metrics.annualized_volatility_percent
        > 0
    )
    assert metrics.maximum_drawdown_percent < 0
    assert metrics.value_at_risk_95_percent >= 0
    assert metrics.largest_position_symbol == "TCS"
    assert (
        metrics.largest_position_weight_percent
        == Decimal("100.00")
    )


def test_multi_stock_returns_are_weighted():
    tcs_returns = build_returns(
        ["0.01", "0.02", "-0.01"]
    )

    infy_returns = build_returns(
        ["-0.01", "0.01", "0.02"]
    )

    metrics = calculate_portfolio_risk(
        portfolio_id="portfolio-test",
        position_values={
            "TCS": Decimal("75000"),
            "INFY": Decimal("25000"),
        },
        returns_by_symbol={
            "TCS": tcs_returns,
            "INFY": infy_returns,
        },
    )

    assert metrics.open_position_count == 2
    assert metrics.largest_position_symbol == "TCS"
    assert (
        metrics.largest_position_weight_percent
        == Decimal("75.00")
    )


def test_empty_portfolio_has_zero_risk():
    metrics = calculate_portfolio_risk(
        portfolio_id="portfolio-empty",
        position_values={},
        returns_by_symbol={},
    )

    assert metrics.observation_count == 0
    assert (
        metrics.annualized_volatility_percent
        == Decimal("0")
    )
    assert metrics.sharpe_ratio is None
    assert metrics.open_position_count == 0