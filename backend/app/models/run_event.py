from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.conversation import utc_now
from app.models.enums import EventType


class RunEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    sequence: int = Field(gt=0)
    type: EventType
    payload: dict[str, Any]
    created_at: datetime = Field(default_factory=utc_now)