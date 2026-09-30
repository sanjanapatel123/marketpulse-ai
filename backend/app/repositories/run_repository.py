from datetime import datetime, timezone
from typing import Any

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.core.database import database
from app.models.enums import EventType, RunStatus
from app.models.run_event import RunEvent


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


async def find_run(run_id: str) -> dict | None:
    return await database.runs.find_one(
        {"id": run_id},
        {"_id": 0},
    )


async def find_message_by_id(message_id: str) -> dict | None:
    return await database.messages.find_one(
        {"id": message_id},
        {"_id": 0},
    )


async def claim_run_for_generation(run_id: str) -> dict | None:
    return await database.runs.find_one_and_update(
        {
            "id": run_id,
            "status": RunStatus.RUNNING.value,
            "generation_claimed_at": None,
        },
        {
            "$set": {
                "generation_claimed_at": utc_now(),
            }
        },
        return_document=ReturnDocument.AFTER,
        projection={"_id": 0},
    )


async def persist_event(
    *,
    run_id: str,
    sequence: int,
    event_type: EventType,
    payload: dict[str, Any],
) -> dict:
    event = RunEvent(
        run_id=run_id,
        sequence=sequence,
        type=event_type,
        payload=payload,
    )

    document = event.model_dump(mode="python")

    try:
        await database.run_events.insert_one(document)
    except DuplicateKeyError:
        existing_event = await database.run_events.find_one(
            {
                "run_id": run_id,
                "sequence": sequence,
            },
            {"_id": 0},
        )

        if (
            existing_event is None
            or existing_event["type"] != event_type.value
            or existing_event["payload"] != payload
        ):
            raise RuntimeError(
                f"Conflicting event at sequence {sequence}"
            )

        return existing_event

    await database.runs.update_one(
        {
            "id": run_id,
            "status": RunStatus.RUNNING.value,
        },
        {
            "$max": {
                "last_sequence": sequence,
            }
        },
    )

    document.pop("_id", None)
    return document


async def mark_run_completed(
    run_id: str,
    last_sequence: int,
) -> bool:
    result = await database.runs.update_one(
        {
            "id": run_id,
            "status": RunStatus.RUNNING.value,
        },
        {
            "$set": {
                "status": RunStatus.COMPLETED.value,
                "completed_at": utc_now(),
                "last_sequence": last_sequence,
                "error_message": None,
            }
        },
    )

    return result.modified_count == 1


async def mark_run_failed(
    run_id: str,
    error_message: str,
    last_sequence: int,
) -> bool:
    result = await database.runs.update_one(
        {
            "id": run_id,
            "status": RunStatus.RUNNING.value,
        },
        {
            "$set": {
                "status": RunStatus.FAILED.value,
                "failed_at": utc_now(),
                "last_sequence": last_sequence,
                "error_message": error_message,
            }
        },
    )

    return result.modified_count == 1

async def find_events_after(
    run_id: str,
    cursor: int,
) -> list[dict]:
    return await database.run_events.find(
        {
            "run_id": run_id,
            "sequence": {
                "$gt": cursor,
            },
        },
        {
            "_id": 0,
        },
    ).sort("sequence", 1).to_list(length=None)


async def find_event_at_sequence(
    run_id: str,
    sequence: int,
) -> dict | None:
    return await database.run_events.find_one(
        {
            "run_id": run_id,
            "sequence": sequence,
        },
        {
            "_id": 0,
        },
    )

async def find_runs_by_status(
    status_value: RunStatus,
) -> list[dict]:
    return await database.runs.find(
        {
            "status": status_value.value,
        },
        {
            "_id": 0,
        },
    ).to_list(length=None)


async def mark_run_interrupted(
    run_id: str,
    reason: str,
    last_sequence: int,
) -> bool:
    result = await database.runs.update_one(
        {
            "id": run_id,
            "status": RunStatus.RUNNING.value,
        },
        {
            "$set": {
                "status": RunStatus.INTERRUPTED.value,
                "interrupted_at": utc_now(),
                "last_sequence": last_sequence,
                "error_message": reason,
            }
        },
    )

    return result.modified_count == 1