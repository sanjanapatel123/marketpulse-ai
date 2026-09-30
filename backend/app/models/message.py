from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.conversation import utc_now
from app.models.enums import MessageRole


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    conversation_id: str
    role: MessageRole
    stock_symbol: str
    content: str
    created_at: datetime = Field(default_factory=utc_now)