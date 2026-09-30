from pydantic import BaseModel, Field, field_validator


class CreateAnalysisRequest(BaseModel):
    conversation_id: str | None = None
    message_id: str | None = None

    stock_symbol: str = Field(min_length=1, max_length=20)
    question: str = Field(min_length=1, max_length=2000)

    @field_validator("stock_symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.strip().upper()


class CreateAnalysisResponse(BaseModel):
    conversation_id: str
    message_id: str
    run_id: str
    status: str
    stream_url: str