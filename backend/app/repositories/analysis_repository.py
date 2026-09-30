from pymongo import ReturnDocument

from app.core.database import database
from app.models.conversation import Conversation
from app.models.enums import MessageRole
from app.models.message import Message
from app.models.run import Run


async def find_message(message_id: str) -> dict | None:
    return await database.messages.find_one(
        {"id": message_id},
        {"_id": 0},
    )


async def find_run_by_message(message_id: str) -> dict | None:
    return await database.runs.find_one(
        {"user_message_id": message_id},
        {"_id": 0},
    )


async def find_conversation(conversation_id: str) -> dict | None:
    return await database.conversations.find_one(
        {"id": conversation_id},
        {"_id": 0},
    )


async def create_conversation() -> dict:
    conversation = Conversation()
    document = conversation.model_dump(mode="python")

    await database.conversations.insert_one(document)

    return document


async def create_or_get_message(
    *,
    message_id: str,
    conversation_id: str,
    stock_symbol: str,
    content: str,
) -> dict:
    message = Message(
        id=message_id,
        conversation_id=conversation_id,
        role=MessageRole.USER,
        stock_symbol=stock_symbol,
        content=content,
    )

    return await database.messages.find_one_and_update(
        {"id": message_id},
        {
            "$setOnInsert": message.model_dump(mode="python"),
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
        projection={"_id": 0},
    )


async def create_or_get_run(
    *,
    conversation_id: str,
    message_id: str,
) -> dict:
    run = Run(
        conversation_id=conversation_id,
        user_message_id=message_id,
    )

    return await database.runs.find_one_and_update(
        {"user_message_id": message_id},
        {
            "$setOnInsert": run.model_dump(mode="python"),
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
        projection={"_id": 0},
    )