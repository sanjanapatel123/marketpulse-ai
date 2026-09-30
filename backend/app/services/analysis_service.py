from uuid import uuid4

from fastapi import HTTPException, status

from app.models.schemas import (
    CreateAnalysisRequest,
    CreateAnalysisResponse,
)
from app.repositories.analysis_repository import (
    create_conversation,
    create_or_get_message,
    create_or_get_run,
    find_conversation,
    find_message,
    find_run_by_message,
)


async def create_analysis(
    payload: CreateAnalysisRequest,
) -> CreateAnalysisResponse:
    message_id = payload.message_id or str(uuid4())

    existing_message = await find_message(message_id)

    if existing_message:
        if (
            existing_message["stock_symbol"] != payload.stock_symbol
            or existing_message["content"] != payload.question
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "This message_id is already associated with "
                    "different message content"
                ),
            )

        existing_run = await find_run_by_message(message_id)

        if existing_run:
            return build_response(existing_run)

    if payload.conversation_id:
        conversation = await find_conversation(
            payload.conversation_id
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
    else:
        conversation = await create_conversation()

    message = await create_or_get_message(
        message_id=message_id,
        conversation_id=conversation["id"],
        stock_symbol=payload.stock_symbol,
        content=payload.question,
    )

    # Protect against reusing the same message ID in another conversation.
    if message["conversation_id"] != conversation["id"]:
        conversation = await find_conversation(
            message["conversation_id"]
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Message references an unavailable conversation",
            )

    run = await create_or_get_run(
        conversation_id=conversation["id"],
        message_id=message["id"],
    )

    return build_response(run)


def build_response(run: dict) -> CreateAnalysisResponse:
    run_id = run["id"]

    return CreateAnalysisResponse(
        conversation_id=run["conversation_id"],
        message_id=run["user_message_id"],
        run_id=run_id,
        status=run["status"],
        stream_url=f"/api/runs/{run_id}/events",
    )