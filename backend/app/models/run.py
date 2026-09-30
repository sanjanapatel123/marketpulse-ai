from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.conversation import utc_now
from app.models.enums import RunStatus


class Run(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    conversation_id: str
    user_message_id: str

    status: RunStatus = RunStatus.RUNNING
    last_sequence: int = 0
    generation_claimed_at: datetime | None = None


    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    failed_at: datetime | None = None
    interrupted_at: datetime | None = None
    error_message: str | None = None