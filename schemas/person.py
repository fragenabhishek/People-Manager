"""Person/contact request/response schemas."""
from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class PersonCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = ""
    phone: Optional[str] = ""
    company: Optional[str] = ""
    job_title: Optional[str] = ""
    location: Optional[str] = ""
    linkedin_url: Optional[str] = ""
    twitter_handle: Optional[str] = ""
    website: Optional[str] = ""
    details: Optional[str] = ""
    how_we_met: Optional[str] = ""
    profile_image_url: Optional[str] = ""
    birthday: Optional[str] = ""
    anniversary: Optional[str] = ""
    met_at: Optional[str] = ""
    tags: Optional[Union[List[str], str]] = []
    next_follow_up: Optional[str] = ""
    follow_up_frequency_days: Optional[int] = 0

    @field_validator("tags", mode="before")
    @classmethod
    def coerce_tags(cls, v: Any) -> list:
        if isinstance(v, str):
            return [t.strip() for t in v.split(",") if t.strip()]
        return v or []


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    website: Optional[str] = None
    details: Optional[str] = None
    how_we_met: Optional[str] = None
    profile_image_url: Optional[str] = None
    birthday: Optional[str] = None
    anniversary: Optional[str] = None
    met_at: Optional[str] = None
    tags: Optional[Union[List[str], str]] = None
    next_follow_up: Optional[str] = None
    follow_up_frequency_days: Optional[int] = None

    @field_validator("tags", mode="before")
    @classmethod
    def coerce_tags(cls, v: Any) -> Optional[list]:
        if v is None:
            return None
        if isinstance(v, str):
            return [t.strip() for t in v.split(",") if t.strip()]
        return v


class TagsRequest(BaseModel):
    tags: List[str] = []


class FollowUpRequest(BaseModel):
    date: Optional[str] = ""
    frequency_days: Optional[int] = 0
