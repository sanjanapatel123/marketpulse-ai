import asyncio
from collections.abc import AsyncGenerator

from fastapi import Request

from app.repositories.notification_repository import (
    list_notifications_after_cursor,
)


NOTIFICATION_POLL_INTERVAL_SECONDS = 0.5


async def stream_notification_events(
    request: Request,
    cursor: int,
) -> AsyncGenerator[dict[str, str], None]:
    """
    Replays durable events after cursor and then continues
    polling the same durable event log for live events.

    MongoDB remains the source of truth for both replay and
    live delivery.
    """
    current_cursor = cursor

    while True:
        if await request.is_disconnected():
            break

        events = await list_notifications_after_cursor(
            cursor=current_cursor,
            limit=100,
        )

        if events:
            for event in events:
                if await request.is_disconnected():
                    return

                yield {
                    "id": str(event.sequence),
                    "event": event.type.value,
                    "data": event.model_dump_json(),
                }

                current_cursor = event.sequence

            # Immediately check for another batch instead of
            # sleeping when replay contains more than 100 events.
            continue

        await asyncio.sleep(
            NOTIFICATION_POLL_INTERVAL_SECONDS
        )