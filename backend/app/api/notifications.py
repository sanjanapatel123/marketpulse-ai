from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Query,
    Request,
    status,
)
from sse_starlette.sse import EventSourceResponse

from app.models.notification import (
    NotificationHistoryResponse,
)
from app.repositories.notification_repository import (
    get_latest_notification_cursor,
    list_recent_notifications,
)
from app.services.notification_cursor_service import (
    validate_notification_cursor,
)
from app.services.notification_stream_service import (
    stream_notification_events,
)


router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"],
)


def resolve_cursor(
    query_cursor: int | None,
    last_event_id: str | None,
) -> int:
    """
    Query cursor is used for the initial connection.
    Last-Event-ID is automatically sent by EventSource on
    some browser reconnections.
    """
    if query_cursor is not None:
        return query_cursor

    if last_event_id is None or not last_event_id.strip():
        return 0

    try:
        cursor = int(last_event_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_CURSOR",
                "message": (
                    "Last-Event-ID must be an integer."
                ),
                "recoverable": True,
            },
        ) from error

    if cursor < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_CURSOR",
                "message": (
                    "Cursor cannot be negative."
                ),
                "recoverable": True,
            },
        )

    return cursor


@router.get(
    "",
    response_model=NotificationHistoryResponse,
)
async def get_notification_history(
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
) -> NotificationHistoryResponse:
    events = await list_recent_notifications(
        limit=limit
    )

    latest_cursor = (
        await get_latest_notification_cursor()
    )

    return NotificationHistoryResponse(
        events=events,
        count=len(events),
        latest_cursor=latest_cursor,
    )


@router.get("/events")
async def get_notification_events(
    request: Request,
    cursor: int | None = Query(
        default=None,
        ge=0,
    ),
    last_event_id: str | None = Header(
        default=None,
        alias="Last-Event-ID",
    ),
) -> EventSourceResponse:
    resolved_cursor = resolve_cursor(
        query_cursor=cursor,
        last_event_id=last_event_id,
    )

    cursor_error = (
        await validate_notification_cursor(
            resolved_cursor
        )
    )

    if cursor_error is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": cursor_error.code,
                "message": cursor_error.message,
                "recoverable": True,
                "earliest_available_cursor": (
                    cursor_error.earliest_cursor
                ),
                "latest_available_cursor": (
                    cursor_error.latest_cursor
                ),
            },
        )

    return EventSourceResponse(
        stream_notification_events(
            request=request,
            cursor=resolved_cursor,
        ),
        ping=15,
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )