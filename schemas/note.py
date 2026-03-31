"""Note request/response schemas."""
from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1)
    note_type: str = "general"


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
