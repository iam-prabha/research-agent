from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class ResearchRequest(BaseModel):
    query: str


class ResearchSessionResponse(BaseModel):
    id: UUID
    query: str
    status: str
    report_markdown: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SSEEvent(BaseModel):
    event: str  # status, warning, progress, claim, done, error
    data: dict
