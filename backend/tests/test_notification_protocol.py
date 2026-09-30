from datetime import UTC, datetime

import pytest
from fastapi import HTTPException

from app.api.notifications import resolve_cursor
from app.models.notification import (
    NotificationEvent,
    NotificationEventType,
    NotificationPayload,
)
from app.services.notification_cursor_service import (
    validate_notification_cursor,
)
from app.services.notification_stream_service import (
    stream_notification_events,
)


FIXED_TIME = datetime(
    2026,
    9,
    30,
    12,
    0,
    tzinfo=UTC,
)


def create_notification_event(
    sequence: int,
) -> NotificationEvent:
    return NotificationEvent(
        id=f"notification-{sequence}",
        sequence=sequence,
        type=(
            NotificationEventType
            .PRICE_ALERT_TRIGGERED
        ),
        source_type="price_alert",
        source_id=f"alert-{sequence}",
        payload=NotificationPayload(
            alert_id=f"alert-{sequence}",
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
        ),
        created_at=FIXED_TIME,
    )


class ConnectedRequest:
    async def is_disconnected(self) -> bool:
        return False


@pytest.mark.asyncio
async def test_notification_stream_delivers_ordered_events(
    monkeypatch: pytest.MonkeyPatch,
):
    events = [
        create_notification_event(1),
        create_notification_event(2),
        create_notification_event(3),
    ]

    requested_cursors: list[int] = []

    async def fake_list_after_cursor(
        cursor: int,
        limit: int,
    ) -> list[NotificationEvent]:
        requested_cursors.append(cursor)

        return [
            event
            for event in events
            if event.sequence > cursor
        ]

    monkeypatch.setattr(
        (
            "app.services.notification_stream_service."
            "list_notifications_after_cursor"
        ),
        fake_list_after_cursor,
    )

    stream = stream_notification_events(
        request=ConnectedRequest(),  # type: ignore[arg-type]
        cursor=0,
    )

    received = [
        await anext(stream),
        await anext(stream),
        await anext(stream),
    ]

    await stream.aclose()

    assert [
        int(event["id"])
        for event in received
    ] == [1, 2, 3]

    assert all(
        event["event"]
        == "price_alert_triggered"
        for event in received
    )

    assert requested_cursors == [0]


@pytest.mark.asyncio
async def test_replay_transitions_to_live_without_duplicates(
    monkeypatch: pytest.MonkeyPatch,
):
    replay_event = create_notification_event(2)
    live_event = create_notification_event(3)

    requested_cursors: list[int] = []

    async def fake_list_after_cursor(
        cursor: int,
        limit: int,
    ) -> list[NotificationEvent]:
        requested_cursors.append(cursor)

        if cursor == 1:
            return [replay_event]

        if cursor == 2:
            return [live_event]

        return []

    monkeypatch.setattr(
        (
            "app.services.notification_stream_service."
            "list_notifications_after_cursor"
        ),
        fake_list_after_cursor,
    )

    stream = stream_notification_events(
        request=ConnectedRequest(),  # type: ignore[arg-type]
        cursor=1,
    )

    replayed = await anext(stream)
    live = await anext(stream)

    await stream.aclose()

    assert int(replayed["id"]) == 2
    assert int(live["id"]) == 3

    # After delivering sequence 2, the next database query
    # must use cursor 2—not the original cursor 1.
    assert requested_cursors == [1, 2]

    assert len(
        {
            replayed["id"],
            live["id"],
        }
    ) == 2


def test_query_cursor_takes_precedence():
    cursor = resolve_cursor(
        query_cursor=7,
        last_event_id="4",
    )

    assert cursor == 7


def test_last_event_id_is_used_for_reconnection():
    cursor = resolve_cursor(
        query_cursor=None,
        last_event_id="12",
    )

    assert cursor == 12


def test_invalid_last_event_id_is_explicit():
    with pytest.raises(HTTPException) as error:
        resolve_cursor(
            query_cursor=None,
            last_event_id="not-an-integer",
        )

    assert error.value.status_code == 400
    assert (
        error.value.detail["code"]
        == "INVALID_CURSOR"
    )
    assert error.value.detail["recoverable"] is True


@pytest.mark.asyncio
async def test_unknown_future_cursor_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
):
    async def fake_bounds():
        return 1, 10

    monkeypatch.setattr(
        (
            "app.services.notification_cursor_service."
            "get_notification_cursor_bounds"
        ),
        fake_bounds,
    )

    result = await validate_notification_cursor(
        cursor=99
    )

    assert result is not None
    assert result.code == "UNKNOWN_CURSOR"
    assert result.earliest_cursor == 1
    assert result.latest_cursor == 10


@pytest.mark.asyncio
async def test_stale_expired_cursor_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
):
    async def fake_bounds():
        # Production retention has removed sequences 1–50.
        return 51, 100

    monkeypatch.setattr(
        (
            "app.services.notification_cursor_service."
            "get_notification_cursor_bounds"
        ),
        fake_bounds,
    )

    result = await validate_notification_cursor(
        cursor=20
    )

    assert result is not None
    assert result.code == "STALE_CURSOR"
    assert result.earliest_cursor == 51
    assert result.latest_cursor == 100


@pytest.mark.asyncio
async def test_retention_boundary_cursor_is_valid(
    monkeypatch: pytest.MonkeyPatch,
):
    async def fake_bounds():
        return 51, 100

    monkeypatch.setattr(
        (
            "app.services.notification_cursor_service."
            "get_notification_cursor_bounds"
        ),
        fake_bounds,
    )

    # Cursor 50 means: deliver everything after 50.
    # The earliest retained event is 51, so replay is safe.
    result = await validate_notification_cursor(
        cursor=50
    )

    assert result is None


@pytest.mark.asyncio
async def test_existing_cursor_is_valid(
    monkeypatch: pytest.MonkeyPatch,
):
    existing_event = create_notification_event(5)

    async def fake_bounds():
        return 1, 10

    async def fake_find(sequence: int):
        if sequence == 5:
            return existing_event

        return None

    monkeypatch.setattr(
        (
            "app.services.notification_cursor_service."
            "get_notification_cursor_bounds"
        ),
        fake_bounds,
    )

    monkeypatch.setattr(
        (
            "app.services.notification_cursor_service."
            "find_notification_at_sequence"
        ),
        fake_find,
    )

    result = await validate_notification_cursor(
        cursor=5
    )

    assert result is None