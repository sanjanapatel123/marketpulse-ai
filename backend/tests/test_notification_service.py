from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.models.watchlist import (
    Currency,
    Exchange,
    PriceAlert,
    PriceAlertCondition,
    PriceAlertStatus,
)
from app.services.notification_service import (
    build_price_alert_notification_payload,
)


def create_triggered_alert() -> PriceAlert:
    now = datetime.now(UTC)

    return PriceAlert(
        id="alert-001",
        watchlist_id="watchlist-001",
        symbol="TCS",
        exchange=Exchange.NSE,
        currency=Currency.INR,
        condition=(
            PriceAlertCondition.PRICE_BELOW
        ),
        threshold=Decimal("4300.00"),
        status=PriceAlertStatus.TRIGGERED,
        triggered_price=Decimal("4215.60"),
        triggered_at=now,
        created_at=now,
        updated_at=now,
    )


def test_build_price_alert_notification_payload():
    alert = create_triggered_alert()

    payload = (
        build_price_alert_notification_payload(
            alert
        )
    )

    assert payload.alert_id == "alert-001"
    assert payload.symbol == "TCS"
    assert payload.condition == "PRICE_BELOW"
    assert payload.threshold == "4300.00"
    assert payload.triggered_price == "4215.60"

    assert payload.title == (
        "TCS price alert triggered"
    )

    assert payload.message == (
        "TCS moved below ₹4,300.00 "
        "at ₹4,215.60."
    )


def test_notification_payload_requires_triggered_price():
    alert = create_triggered_alert()
    alert.triggered_price = None

    with pytest.raises(
        ValueError,
        match=(
            "Triggered alert must have "
            "triggered_price"
        ),
    ):
        build_price_alert_notification_payload(
            alert
        )