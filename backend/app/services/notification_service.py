from decimal import Decimal, InvalidOperation
from enum import Enum

from app.models.notification import (
    NotificationEvent,
    NotificationEventType,
    NotificationPayload,
)
from app.models.watchlist import PriceAlert
from app.repositories.notification_repository import (
    create_notification_event,
)
from app.repositories.watchlist_repository import (
    list_triggered_price_alerts,
)


def _enum_value(value: object) -> str:
    if isinstance(value, Enum):
        return str(value.value)

    return str(value)


def _money(value: object) -> str:
    try:
        amount = Decimal(str(value))

        return f"{amount:,.2f}"
    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):
        return str(value)


def build_price_alert_notification_payload(
    alert: PriceAlert,
) -> NotificationPayload:
    if alert.triggered_price is None:
        raise ValueError(
            "Triggered alert must have triggered_price"
        )

    condition = _enum_value(alert.condition)
    exchange = _enum_value(alert.exchange)
    currency = _enum_value(alert.currency)

    direction = (
        "above"
        if condition == "PRICE_ABOVE"
        else "below"
    )

    threshold = str(alert.threshold)
    triggered_price = str(alert.triggered_price)

    title = (
        f"{alert.symbol} price alert triggered"
    )

    message = (
        f"{alert.symbol} moved {direction} "
        f"₹{_money(alert.threshold)} at "
        f"₹{_money(alert.triggered_price)}."
    )

    return NotificationPayload(
        alert_id=alert.id,
        watchlist_id=alert.watchlist_id,
        symbol=alert.symbol,
        exchange=exchange,
        currency=currency,
        condition=condition,
        threshold=threshold,
        triggered_price=triggered_price,
        title=title,
        message=message,
    )


async def publish_price_alert_notification(
    alert: PriceAlert,
) -> NotificationEvent:
    payload = (
        build_price_alert_notification_payload(
            alert
        )
    )

    return await create_notification_event(
        event_type=(
            NotificationEventType
            .PRICE_ALERT_TRIGGERED
        ),
        source_type="price_alert",
        source_id=alert.id,
        payload=payload,
    )


async def reconcile_price_alert_notifications(
) -> list[NotificationEvent]:
    """
    Ensures every triggered price alert has exactly one
    durable notification.

    Existing events are returned idempotently by the
    notification repository.
    """
    triggered_alerts = (
        await list_triggered_price_alerts()
    )

    events: list[NotificationEvent] = []

    for alert in triggered_alerts:
        event = (
            await publish_price_alert_notification(
                alert
            )
        )

        events.append(event)

    return events