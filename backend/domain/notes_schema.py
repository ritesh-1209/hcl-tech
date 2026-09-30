from enum import Enum
from typing import List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(str, Enum):
    CONCEPTUAL = "conceptual"
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    CALCULATION = "calculation"
    TRUE_FALSE = "true_false"


class Definition(BaseModel):
    """Domain model for key term definitions."""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        extra="ignore",
    )

    term: str = Field(..., min_length=1, description="Defined term or key word")
    meaning: str = Field(
        ..., min_length=1, description="Definition or explanation of the term"
    )

    @field_validator("term", "meaning")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or contain only whitespace.")
        return v.strip()


class Topic(BaseModel):
    """Domain model representing a single topic within lecture notes."""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        extra="ignore",
    )

    heading: str = Field(..., min_length=1, description="Topic heading or title")
    key_points: List[str] = Field(
        default_factory=list, description="List of key points under this topic"
    )
    definitions: List[Definition] = Field(
        default_factory=list, description="Definitions specific to this topic"
    )
    examples: List[str] = Field(
        default_factory=list, description="Illustrative examples"
    )
    formulas: List[str] = Field(
        default_factory=list, description="Relevant mathematical or logical formulas"
    )
    source_text: Optional[str] = Field(
        default=None, description="Direct quote or source text section"
    )
    source_references: List[str] = Field(
        default_factory=list, description="References to lecture transcript sections"
    )

    @field_validator("heading")
    @classmethod
    def validate_heading(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Topic heading cannot be empty.")
        return v.strip()


class RevisionQuestion(BaseModel):
    """Domain model for self-assessment revision questions."""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
        extra="ignore",
    )

    question: str = Field(..., min_length=1, description="The revision question text")
    answer: str = Field(..., min_length=1, description="The correct answer or model response")
    difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.MEDIUM, description="Question difficulty level"
    )
    question_type: QuestionType = Field(
        default=QuestionType.SHORT_ANSWER, description="Type of question"
    )

    @field_validator("question", "answer")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Question and answer fields cannot be empty.")
        return v.strip()

    @field_validator("difficulty", mode="before")
    @classmethod
    def normalize_difficulty(cls, v: str | DifficultyLevel) -> DifficultyLevel | str:
        if isinstance(v, str):
            v_lower = v.lower()
            for member in DifficultyLevel:
                if member.value == v_lower:
                    return member
        return v

    @field_validator("question_type", mode="before")
    @classmethod
    def normalize_question_type(cls, v: str | QuestionType) -> QuestionType | str:
        if isinstance(v, str):
            v_lower = v.lower()
            for member in QuestionType:
                if member.value == v_lower:
                    return member
        return v


class QualityMetadata(BaseModel):
    """Quality and coverage metadata associated with final notes."""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        extra="ignore",
    )

    coverage_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Topic coverage score (0.0 to 1.0)"
    )
    quality_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Overall quality score (0.0 to 1.0)"
    )
    completeness_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Completeness score (0.0 to 1.0)"
    )
    faithfulness_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Faithfulness to source material score (0.0 to 1.0)",
    )
    word_count: int = Field(default=0, ge=0, description="Total word count in notes")
    topic_count: int = Field(default=0, ge=0, description="Number of topics covered")


class Notes(BaseModel):
    """Domain model representing complete compiled final lecture notes."""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        extra="ignore",
    )

    title: str = Field(..., min_length=1, description="Title of the final notes")
    subject: str = Field(..., min_length=1, description="Subject of the notes")
    overview: str = Field(
        default="", description="Executive summary or high-level overview"
    )
    topics: List[Topic] = Field(
        default_factory=list, description="Structured topics and sub-topics"
    )
    glossary: List[Definition] = Field(
        default_factory=list, description="Consolidated glossary of definitions"
    )
    revision_questions: List[RevisionQuestion] = Field(
        default_factory=list, description="Set of revision questions"
    )
    quality_metadata: QualityMetadata = Field(
        default_factory=QualityMetadata,
        validation_alias=AliasChoices(
            "quality_metadata", "coverage_metadata", "metadata", "quality"
        ),
        description="Quality and coverage metrics",
    )

    @field_validator("title", "subject")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title and subject fields cannot be empty.")
        return v.strip()
