from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.notification import (
    NotificationEvent,
    NotificationEventType,
    NotificationPayload,
)


def create_payload() -> NotificationPayload:
    return NotificationPayload(
        alert_id="alert-001",
        watchlist_id="watchlist-001",
        symbol="TCS",
        exchange="NSE",
        currency="INR",
        condition="PRICE_BELOW",
        threshold="4300.00",
        triggered_price="4215.60",
        title="TCS price alert triggered",
        message=(
            "TCS moved below ₹4,300.00 "
            "at ₹4,215.60."
        ),
    )


def test_notification_event_has_stable_cursor():
    event = NotificationEvent(
        id="notification-001",
        sequence=12,
        type=(
            NotificationEventType
            .PRICE_ALERT_TRIGGERED
        ),
        source_id="alert-001",
        source_type="price_alert",
        payload=create_payload(),
        created_at=datetime.now(UTC),
    )

    assert event.sequence == 12
    assert event.source_id == "alert-001"
    assert event.payload.symbol == "TCS"


def test_notification_sequence_must_be_positive():
    with pytest.raises(ValidationError):
        NotificationEvent(
            id="notification-invalid",
            sequence=0,
            type=(
                NotificationEventType
                .PRICE_ALERT_TRIGGERED
            ),
            source_id="alert-001",
            source_type="price_alert",
            payload=create_payload(),
            created_at=datetime.now(UTC),
        )


def test_notification_serializes_event_type():
    event = NotificationEvent(
        id="notification-001",
        sequence=1,
        type=(
            NotificationEventType
            .PRICE_ALERT_TRIGGERED
        ),
        source_id="alert-001",
        source_type="price_alert",
        payload=create_payload(),
        created_at=datetime.now(UTC),
    )

    serialized = event.model_dump(
        mode="json",
    )

    assert (
        serialized["type"]
        == "price_alert_triggered"
    )