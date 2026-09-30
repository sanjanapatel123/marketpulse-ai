from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Query,
    Request,
    status,
)
from sse_starlette.sse import EventSourceResponse

from app.core.database import database
from app.repositories.run_repository import (
    find_event_at_sequence,
    find_run,
)
from app.services.run_stream_service import stream_run_events

router = APIRouter(
    prefix="/api/runs",
    tags=["Runs"],
)


@router.get("/{run_id}")
async def get_run(run_id: str):
    run = await find_run(run_id)

    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )

    events = await database.run_events.find(
        {"run_id": run_id},
        {"_id": 0},
    ).sort("sequence", 1).to_list(length=None)

    return {
        "run": run,
        "events": events,
        "event_count": len(events),
    }


@router.get("/{run_id}/events")
async def get_run_events(
    request: Request,
    run_id: str,
    cursor: int | None = Query(default=None, ge=0),
    last_event_id: str | None = Header(
        default=None,
        alias="Last-Event-ID",
    ),
):
    run = await find_run(run_id)

    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RUN_NOT_FOUND",
                "message": "Run not found",
                "recoverable": False,
            },
        )

    resolved_cursor = resolve_cursor(
        query_cursor=cursor,
        last_event_id=last_event_id,
    )

    await validate_cursor(
        run=run,
        cursor=resolved_cursor,
    )

    return EventSourceResponse(
        stream_run_events(
            request=request,
            run_id=run_id,
            initial_cursor=resolved_cursor,
        ),
        ping=10,
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
        },
    )


def resolve_cursor(
    *,
    query_cursor: int | None,
    last_event_id: str | None,
) -> int:
    if query_cursor is not None:
        return query_cursor

    if last_event_id is None or last_event_id == "":
        return 0

    try:
        cursor = int(last_event_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_CURSOR",
                "message": "Last-Event-ID must be an integer",
                "recoverable": True,
            },
        ) from error

    if cursor < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_CURSOR",
                "message": "Cursor cannot be negative",
                "recoverable": True,
            },
        )

    return cursor


async def validate_cursor(
    *,
    run: dict,
    cursor: int,
) -> None:
    if cursor == 0:
        return

    if cursor > run["last_sequence"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "CURSOR_AHEAD_OF_RUN",
                "message": (
                    f"Cursor {cursor} is ahead of the run's "
                    f"last sequence {run['last_sequence']}"
                ),
                "recoverable": True,
                "restart_cursor": 0,
            },
        )

    cursor_event = await find_event_at_sequence(
        run_id=run["id"],
        sequence=cursor,
    )

    if cursor_event is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "CURSOR_UNAVAILABLE",
                "message": (
                    f"Event at cursor {cursor} is unavailable"
                ),
                "recoverable": True,
                "restart_cursor": 0,
            },
        )