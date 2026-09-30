from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DetailLevel(str, Enum):
    SUMMARY = "summary"
    BRIEF = "brief"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    DETAILED = "detailed"


class InputType(str, Enum):
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    PDF = "pdf"
    TRANSCRIPT = "transcript"


class Lecture(BaseModel):
    """Domain model representing a lecture input source for note generation."""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
        extra="ignore",
    )

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the lecture",
    )
    title: str = Field(..., min_length=1, description="Title of the lecture")
    subject: str = Field(..., min_length=1, description="Subject or topic category")
    detail_level: DetailLevel = Field(
        default=DetailLevel.STANDARD,
        description="Target detail level for note generation",
    )
    input_type: InputType = Field(
        default=InputType.TEXT,
        description="Format of the input source material",
    )
    transcript: str = Field(
        ..., min_length=1, description="Full lecture transcript or text content"
    )

    @field_validator("id", "title", "subject", "transcript")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or contain only whitespace.")
        return v.strip()

    @field_validator("detail_level", mode="before")
    @classmethod
    def normalize_detail_level(cls, v: str | DetailLevel) -> DetailLevel | str:
        if isinstance(v, str):
            v_lower = v.lower()
            for member in DetailLevel:
                if member.value == v_lower:
                    return member
        return v

    @field_validator("input_type", mode="before")
    @classmethod
    def normalize_input_type(cls, v: str | InputType) -> InputType | str:
        if isinstance(v, str):
            v_lower = v.lower()
            for member in InputType:
                if member.value == v_lower:
                    return member
        return v
