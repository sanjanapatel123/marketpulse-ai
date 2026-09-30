from datetime import UTC, datetime
from uuid import uuid4

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.core.database import database
from app.models.notification import (
    NotificationEvent,
    NotificationEventType,
    NotificationPayload,
)


NOTIFICATION_COUNTER_NAME = "notification_events"


def _deserialize_event(
    document: dict,
) -> NotificationEvent:
    document.pop("_id", None)

    return NotificationEvent.model_validate(
        document
    )


async def _allocate_sequence() -> int:
    """
    Atomically allocates a globally increasing notification
    sequence. The sequence is used as the SSE cursor.
    """
    counter = (
        await database.event_counters.find_one_and_update(
            {
                "name": NOTIFICATION_COUNTER_NAME,
            },
            {
                "$inc": {
                    "value": 1,
                },
                "$setOnInsert": {
                    "created_at": datetime.now(UTC),
                },
                "$set": {
                    "updated_at": datetime.now(UTC),
                },
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
    )

    if counter is None:
        raise RuntimeError(
            "Unable to allocate notification sequence"
        )

    return int(counter["value"])


async def find_notification_by_source(
    source_type: str,
    source_id: str,
) -> NotificationEvent | None:
    document = (
        await database.notification_events.find_one(
            {
                "source_type": source_type,
                "source_id": source_id,
            }
        )
    )

    if document is None:
        return None

    return _deserialize_event(document)


async def create_notification_event(
    *,
    event_type: NotificationEventType,
    source_type: str,
    source_id: str,
    payload: NotificationPayload,
) -> NotificationEvent:
    """
    Creates one logical notification for a source.

    Repeated calls with the same source_type/source_id return
    the already persisted event instead of creating duplicates.
    """
    existing = await find_notification_by_source(
        source_type=source_type,
        source_id=source_id,
    )

    if existing is not None:
        return existing

    sequence = await _allocate_sequence()
    created_at = datetime.now(UTC)

    event = NotificationEvent(
        id=str(uuid4()),
        sequence=sequence,
        type=event_type,
        source_type=source_type,
        source_id=source_id,
        payload=payload,
        created_at=created_at,
    )

    document = event.model_dump(
        mode="python",
    )

    # Store the enum as its wire-format string.
    document["type"] = event.type.value

    try:
        await database.notification_events.insert_one(
            document
        )

        return event

    except DuplicateKeyError:
        # Another concurrent worker may have inserted the same
        # logical source event first.
        existing = await find_notification_by_source(
            source_type=source_type,
            source_id=source_id,
        )

        if existing is None:
            raise

        return existing


async def find_notification_event(
    event_id: str,
) -> NotificationEvent | None:
    document = (
        await database.notification_events.find_one(
            {
                "id": event_id,
            }
        )
    )

    if document is None:
        return None

    return _deserialize_event(document)


async def find_notification_at_sequence(
    sequence: int,
) -> NotificationEvent | None:
    document = (
        await database.notification_events.find_one(
            {
                "sequence": sequence,
            }
        )
    )

    if document is None:
        return None

    return _deserialize_event(document)


async def list_notifications_after_cursor(
    cursor: int,
    limit: int = 100,
) -> list[NotificationEvent]:
    """
    Returns events strictly after the client cursor in
    deterministic server order.
    """
    safe_limit = max(
        1,
        min(limit, 500),
    )

    documents = (
        await database.notification_events.find(
            {
                "sequence": {
                    "$gt": cursor,
                }
            }
        )
        .sort(
            "sequence",
            ASCENDING,
        )
        .limit(safe_limit)
        .to_list(length=safe_limit)
    )

    return [
        _deserialize_event(document)
        for document in documents
    ]


async def list_recent_notifications(
    limit: int = 50,
) -> list[NotificationEvent]:
    safe_limit = max(
        1,
        min(limit, 500),
    )

    documents = (
        await database.notification_events.find({})
        .sort(
            "sequence",
            -1,
        )
        .limit(safe_limit)
        .to_list(length=safe_limit)
    )

    events = [
        _deserialize_event(document)
        for document in documents
    ]

    # API consumers receive deterministic ascending order.
    return sorted(
        events,
        key=lambda event: event.sequence,
    )


async def get_notification_cursor_bounds(
) -> tuple[int | None, int | None]:
    """
    Returns:
        (earliest_available_cursor, latest_available_cursor)

    When no notification exists:
        (None, None)
    """
    earliest_document = (
        await database.notification_events.find_one(
            {},
            sort=[
                ("sequence", ASCENDING),
            ],
            projection={
                "_id": 0,
                "sequence": 1,
            },
        )
    )

    if earliest_document is None:
        return None, None

    latest_document = (
        await database.notification_events.find_one(
            {},
            sort=[
                ("sequence", -1),
            ],
            projection={
                "_id": 0,
                "sequence": 1,
            },
        )
    )

    if latest_document is None:
        return None, None

    return (
        int(earliest_document["sequence"]),
        int(latest_document["sequence"]),
    )


async def get_latest_notification_cursor() -> int:
    _, latest_cursor = (
        await get_notification_cursor_bounds()
    )

    return latest_cursor or 0