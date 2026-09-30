from enum import Enum
from typing import List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class ValidationStatus(str, Enum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CoverageResult(BaseModel):
    """Evaluation result for content coverage against lecture source material."""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        extra="ignore",
    )

    coverage_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Overall coverage score between 0.0 and 1.0",
    )
    covered_topics: List[str] = Field(
        default_factory=list, description="Topics successfully covered in the notes"
    )
    missing_topics: List[str] = Field(
        default_factory=list,
        description="Topics identified in source but missing in notes",
    )
    summary: str = Field(
        default="", description="Summary explanation of coverage evaluation"
    )

    @field_validator("coverage_score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("coverage_score must be between 0.0 and 1.0 inclusive.")
        return v


class FaithfulnessWarning(BaseModel):
    """Warning describing unverified assertions, hallucinations, or contradictions."""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
        extra="ignore",
    )

    warning_type: str = Field(
        ...,
        min_length=1,
        description="Category of faithfulness warning (e.g., hallucination, contradiction)",
    )
    message: str = Field(..., min_length=1, description="Detailed description of the issue")
    severity: SeverityLevel = Field(
        default=SeverityLevel.MEDIUM, description="Severity level of the warning"
    )
    location: Optional[str] = Field(
        default=None, description="Topic or section where the issue was detected"
    )
    suggested_fix: Optional[str] = Field(
        default=None, description="Optional recommendation to resolve the issue"
    )

    @field_validator("warning_type", "message")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Warning fields cannot be empty.")
        return v.strip()

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, v: str | SeverityLevel) -> SeverityLevel | str:
        if isinstance(v, str):
            v_lower = v.lower()
            for member in SeverityLevel:
                if member.value == v_lower:
                    return member
        return v


class ValidationResult(BaseModel):
    """Aggregated validation result for notes quality and faithfulness."""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
        extra="ignore",
    )

    status: ValidationStatus = Field(
        default=ValidationStatus.PASSED, description="Overall validation status"
    )
    is_valid: bool = Field(
        default=True, description="Boolean flag indicating overall validity"
    )
    overall_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Combined quality and faithfulness score"
    )
    coverage: CoverageResult = Field(
        default_factory=CoverageResult,
        validation_alias=AliasChoices("coverage", "coverage_result", "coverage_results"),
        description="Coverage evaluation metrics",
    )
    faithfulness_warnings: List[FaithfulnessWarning] = Field(
        default_factory=list,
        validation_alias=AliasChoices("faithfulness_warnings", "warnings", "faithfulness"),
        description="List of detected faithfulness warnings or hallucinations",
    )
    notes: List[str] = Field(
        default_factory=list, description="General validation notes or feedback"
    )

    @field_validator("overall_score")
    @classmethod
    def validate_overall_score(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("overall_score must be between 0.0 and 1.0 inclusive.")
        return v

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: str | ValidationStatus) -> ValidationStatus | str:
        if isinstance(v, str):
            v_lower = v.lower()
            for member in ValidationStatus:
                if member.value == v_lower:
                    return member
        return v
