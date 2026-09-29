from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: Optional[str]
    owner_id: int
    created_at: datetime
    updated_at: datetime


class PaginatedNotes(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[NoteResponse]
