from dataclasses import dataclass

from app.repositories.notification_repository import (
    find_notification_at_sequence,
    get_notification_cursor_bounds,
)


@dataclass(frozen=True)
class CursorValidationError:
    code: str
    message: str
    earliest_cursor: int | None
    latest_cursor: int | None


async def validate_notification_cursor(
    cursor: int,
) -> CursorValidationError | None:
    if cursor < 0:
        return CursorValidationError(
            code="INVALID_CURSOR",
            message="Cursor cannot be negative.",
            earliest_cursor=None,
            latest_cursor=None,
        )

    earliest, latest = (
        await get_notification_cursor_bounds()
    )

    # Empty stream only accepts cursor zero.
    if earliest is None or latest is None:
        if cursor == 0:
            return None

        return CursorValidationError(
            code="UNKNOWN_CURSOR",
            message=(
                "The notification stream is empty, "
                "so this cursor is unavailable."
            ),
            earliest_cursor=None,
            latest_cursor=None,
        )

    # Cursor zero means replay everything still retained.
    if cursor == 0:
        return None

    # If retention begins at event 51, cursor 50 is valid:
    # it requests replay beginning with event 51.
    if cursor < earliest - 1:
        return CursorValidationError(
            code="STALE_CURSOR",
            message=(
                "The requested cursor is older than "
                "the retained notification history."
            ),
            earliest_cursor=earliest,
            latest_cursor=latest,
        )

    if cursor > latest:
        return CursorValidationError(
            code="UNKNOWN_CURSOR",
            message=(
                "The requested cursor is ahead of "
                "the latest notification event."
            ),
            earliest_cursor=earliest,
            latest_cursor=latest,
        )

    if cursor == earliest - 1:
        return None

    event = await find_notification_at_sequence(
        cursor
    )

    if event is None:
        return CursorValidationError(
            code="UNKNOWN_CURSOR",
            message=(
                "The requested cursor does not identify "
                "an available notification event."
            ),
            earliest_cursor=earliest,
            latest_cursor=latest,
        )

    return None