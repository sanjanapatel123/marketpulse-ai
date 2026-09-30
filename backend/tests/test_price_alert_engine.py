from decimal import Decimal

import pytest

from app.models.enums import PriceAlertCondition
from app.services.price_alert_engine import (
    should_trigger_price_alert,
)


@pytest.mark.parametrize(
    (
        "current_price",
        "threshold",
        "expected",
    ),
    [
        ("4301.00", "4300.00", True),
        ("4300.00", "4300.00", True),
        ("4299.99", "4300.00", False),
    ],
)
def test_price_above_condition(
    current_price: str,
    threshold: str,
    expected: bool,
):
    result = should_trigger_price_alert(
        condition=PriceAlertCondition.PRICE_ABOVE,
        threshold=Decimal(threshold),
        current_price=Decimal(current_price),
    )

    assert result is expected


@pytest.mark.parametrize(
    (
        "current_price",
        "threshold",
        "expected",
    ),
    [
        ("4199.00", "4200.00", True),
        ("4200.00", "4200.00", True),
        ("4200.01", "4200.00", False),
    ],
)
def test_price_below_condition(
    current_price: str,
    threshold: str,
    expected: bool,
):
    result = should_trigger_price_alert(
        condition=PriceAlertCondition.PRICE_BELOW,
        threshold=Decimal(threshold),
        current_price=Decimal(current_price),
    )

    assert result is expected