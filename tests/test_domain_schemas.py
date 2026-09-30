import json
import pytest
from pydantic import ValidationError

from backend.domain.lecture_schema import DetailLevel, InputType, Lecture
from backend.domain.notes_schema import (
    Definition,
    DifficultyLevel,
    Notes,
    QualityMetadata,
    QuestionType,
    RevisionQuestion,
    Topic,
)
from backend.domain.validation_schema import (
    CoverageResult,
    FaithfulnessWarning,
    SeverityLevel,
    ValidationResult,
    ValidationStatus,
)


# ==========================================
# 1. Lecture Schema Tests
# ==========================================

def test_lecture_valid_default_and_custom():
    # Valid lecture with defaults
    lec1 = Lecture(
        title="Introduction to Machine Learning",
        subject="Computer Science",
        transcript="In this lecture, we will cover supervised learning...",
    )
    assert lec1.id is not None
    assert len(lec1.id) > 0
    assert lec1.title == "Introduction to Machine Learning"
    assert lec1.subject == "Computer Science"
    assert lec1.detail_level == DetailLevel.STANDARD
    assert lec1.input_type == InputType.TEXT
    assert "supervised learning" in lec1.transcript

    # Valid lecture with explicit values and enum strings
    lec2 = Lecture(
        id="lec-12345",
        title="  Quantum Mechanics 101  ",
        subject="Physics",
        detail_level="comprehensive",
        input_type="audio",
        transcript="Schrodinger equation explanation...",
    )
    assert lec2.id == "lec-12345"
    assert lec2.title == "Quantum Mechanics 101"  # Stripped whitespace
    assert lec2.detail_level == DetailLevel.COMPREHENSIVE
    assert lec2.input_type == InputType.AUDIO


def test_lecture_missing_required_fields():
    with pytest.raises(ValidationError) as exc_info:
        Lecture(subject="Physics", transcript="Transcript content")
    assert "title" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        Lecture(title="Physics", transcript="Transcript content")
    assert "subject" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        Lecture(title="Physics", subject="Physics")
    assert "transcript" in str(exc_info.value)


def test_lecture_invalid_empty_and_whitespace_values():
    with pytest.raises(ValidationError):
        Lecture(title="", subject="Physics", transcript="Valid transcript")

    with pytest.raises(ValidationError):
        Lecture(title="   ", subject="Physics", transcript="Valid transcript")

    with pytest.raises(ValidationError):
        Lecture(title="Physics", subject="   ", transcript="Valid transcript")

    with pytest.raises(ValidationError):
        Lecture(title="Physics", subject="Physics", transcript="   ")


def test_lecture_llm_json_parsing():
    json_data = json.dumps({
        "id": "custom-id-99",
        "title": "Data Structures",
        "subject": "CS",
        "detail_level": "detailed",
        "input_type": "pdf",
        "transcript": "Binary search trees are hierarchical data structures...",
        "unsupported_extra_field": "should be ignored"
    })
    lec = Lecture.model_validate_json(json_data)
    assert lec.id == "custom-id-99"
    assert lec.title == "Data Structures"
    assert lec.detail_level == DetailLevel.DETAILED
    assert lec.input_type == InputType.PDF


# ==========================================
# 2. Definition & Topic Tests
# ==========================================

def test_definition_valid_and_invalid():
    dfn = Definition(term="Entropy", meaning="Measure of disorder in a system.")
    assert dfn.term == "Entropy"
    assert dfn.meaning == "Measure of disorder in a system."

    with pytest.raises(ValidationError):
        Definition(term="", meaning="Valid meaning")

    with pytest.raises(ValidationError):
        Definition(term="Valid term", meaning="   ")


def test_topic_valid_defaults_and_nested():
    def1 = Definition(term="Gradient Descent", meaning="Optimization algorithm.")
    topic = Topic(
        heading="Optimization Algorithms",
        key_points=["Calculates gradients", "Updates weights iteratively"],
        definitions=[def1],
        examples=["Training a linear regression model"],
        formulas=["theta = theta - alpha * grad"],
        source_text="Gradient descent minimizes cost function...",
        source_references=["00:12:30 - 00:15:45"]
    )
    assert topic.heading == "Optimization Algorithms"
    assert len(topic.key_points) == 2
    assert topic.definitions[0].term == "Gradient Descent"
    assert len(topic.examples) == 1
    assert len(topic.formulas) == 1
    assert topic.source_text is not None

    # Empty defaults
    minimal_topic = Topic(heading="Minimal Topic")
    assert minimal_topic.key_points == []
    assert minimal_topic.definitions == []
    assert minimal_topic.examples == []
    assert minimal_topic.formulas == []
    assert minimal_topic.source_text is None
    assert minimal_topic.source_references == []


def test_topic_invalid_heading():
    with pytest.raises(ValidationError):
        Topic(heading="  ")


# ==========================================
# 3. RevisionQuestion Tests
# ==========================================

def test_revision_question_valid_and_defaults():
    rq = RevisionQuestion(
        question="What is backpropagation?",
        answer="An algorithm to compute gradients of the loss function."
    )
    assert rq.question == "What is backpropagation?"
    assert rq.answer == "An algorithm to compute gradients of the loss function."
    assert rq.difficulty == DifficultyLevel.MEDIUM
    assert rq.question_type == QuestionType.SHORT_ANSWER


def test_revision_question_custom_enums():
    rq = RevisionQuestion(
        question="State Newton's Second Law.",
        answer="F = ma",
        difficulty="easy",
        question_type="conceptual"
    )
    assert rq.difficulty == DifficultyLevel.EASY
    assert rq.question_type == QuestionType.CONCEPTUAL


def test_revision_question_invalid_values():
    with pytest.raises(ValidationError):
        RevisionQuestion(question="", answer="Answer text")

    with pytest.raises(ValidationError):
        RevisionQuestion(question="Question text", answer="   ")


# ==========================================
# 4. QualityMetadata & Notes Tests
# ==========================================

def test_quality_metadata_valid_and_out_of_bounds():
    qm = QualityMetadata(
        coverage_score=0.95,
        quality_score=0.90,
        word_count=1200,
        topic_count=5
    )
    assert qm.coverage_score == 0.95
    assert qm.word_count == 1200

    # Invalid coverage score > 1.0
    with pytest.raises(ValidationError):
        QualityMetadata(coverage_score=1.5)

    # Invalid coverage score < 0.0
    with pytest.raises(ValidationError):
        QualityMetadata(coverage_score=-0.1)

    # Invalid word count < 0
    with pytest.raises(ValidationError):
        QualityMetadata(word_count=-10)


def test_notes_nested_structure():
    def1 = Definition(term="Supervised Learning", meaning="Learning with labeled data.")
    topic1 = Topic(
        heading="Supervised Learning Overview",
        key_points=["Requires targets", "Includes regression and classification"],
        definitions=[def1]
    )
    rq1 = RevisionQuestion(
        question="What distinguishes supervised from unsupervised learning?",
        answer="Supervised learning uses labeled dataset targets.",
        difficulty=DifficultyLevel.EASY
    )
    metadata = QualityMetadata(coverage_score=0.98, quality_score=0.95, word_count=500, topic_count=1)

    notes = Notes(
        title="Machine Learning Foundations",
        subject="Computer Science",
        overview="Comprehensive notes covering supervised learning principles.",
        topics=[topic1],
        glossary=[def1],
        revision_questions=[rq1],
        quality_metadata=metadata
    )

    assert notes.title == "Machine Learning Foundations"
    assert len(notes.topics) == 1
    assert notes.topics[0].definitions[0].term == "Supervised Learning"
    assert len(notes.glossary) == 1
    assert len(notes.revision_questions) == 1
    assert notes.quality_metadata.coverage_score == 0.98


def test_notes_missing_required_fields():
    with pytest.raises(ValidationError):
        Notes(subject="CS")

    with pytest.raises(ValidationError):
        Notes(title="ML Notes")


def test_notes_invalid_fields():
    with pytest.raises(ValidationError):
        Notes(title="", subject="CS")

    with pytest.raises(ValidationError):
        Notes(title="ML Notes", subject="   ")


def test_notes_llm_json_direct_parsing():
    raw_llm_json = json.dumps({
        "title": "Thermodynamics Core Notes",
        "subject": "Physics",
        "overview": "Summary of 1st and 2nd laws of thermodynamics.",
        "topics": [
            {
                "heading": "First Law of Thermodynamics",
                "key_points": ["Energy cannot be created or destroyed", "Delta U = Q - W"],
                "definitions": [
                    {"term": "Internal Energy", "meaning": "Total microscopic energy of a system."}
                ],
                "examples": ["Piston expansion"],
                "formulas": ["dU = dQ - dW"]
            }
        ],
        "glossary": [
            {"term": "Entropy", "meaning": "State function representing system randomness."}
        ],
        "revision_questions": [
            {
                "question": "What is the formula for the first law?",
                "answer": "Delta U = Q - W",
                "difficulty": "medium",
                "question_type": "short_answer"
            }
        ],
        "coverage_metadata": {
            "coverage_score": 0.92,
            "quality_score": 0.88,
            "word_count": 350,
            "topic_count": 1
        }
    })

    notes = Notes.model_validate_json(raw_llm_json)
    assert notes.title == "Thermodynamics Core Notes"
    assert notes.topics[0].heading == "First Law of Thermodynamics"
    assert notes.topics[0].definitions[0].term == "Internal Energy"
    assert notes.glossary[0].term == "Entropy"
    assert notes.revision_questions[0].difficulty == DifficultyLevel.MEDIUM
    assert notes.quality_metadata.coverage_score == 0.92


# ==========================================
# 5. Validation Schema Tests
# ==========================================

def test_coverage_result_valid_and_invalid():
    cov = CoverageResult(
        coverage_score=0.85,
        covered_topics=["Linear Algebra", "Vector Spaces"],
        missing_topics=["Eigenvalues"],
        summary="Good overall coverage with minor missing subtopic."
    )
    assert cov.coverage_score == 0.85
    assert len(cov.covered_topics) == 2
    assert len(cov.missing_topics) == 1

    with pytest.raises(ValidationError):
        CoverageResult(coverage_score=1.2)


def test_faithfulness_warning_valid_and_invalid():
    warning = FaithfulnessWarning(
        warning_type="hallucination",
        message="Claim about 100% accuracy is not present in lecture source.",
        severity="high",
        location="Topic 2: Performance Evaluation"
    )
    assert warning.warning_type == "hallucination"
    assert warning.severity == SeverityLevel.HIGH
    assert warning.location == "Topic 2: Performance Evaluation"

    with pytest.raises(ValidationError):
        FaithfulnessWarning(warning_type="", message="Valid message")

    with pytest.raises(ValidationError):
        FaithfulnessWarning(warning_type="hallucination", message="  ")


def test_validation_result_nested_and_defaults():
    cov = CoverageResult(coverage_score=0.90, covered_topics=["Topic A"])
    warning = FaithfulnessWarning(
        warning_type="unverified_assertion",
        message="Specific stat not found in transcript",
        severity=SeverityLevel.LOW
    )

    val_res = ValidationResult(
        status="warning",
        is_valid=True,
        overall_score=0.88,
        coverage=cov,
        faithfulness_warnings=[warning],
        notes=["Minor warning found during verification"]
    )

    assert val_res.status == ValidationStatus.WARNING
    assert val_res.is_valid is True
    assert val_res.overall_score == 0.88
    assert val_res.coverage.coverage_score == 0.90
    assert len(val_res.faithfulness_warnings) == 1
    assert val_res.faithfulness_warnings[0].severity == SeverityLevel.LOW


def test_validation_result_invalid_overall_score():
    with pytest.raises(ValidationError):
        ValidationResult(overall_score=-0.5)


def test_validation_result_llm_json_parsing():
    json_str = json.dumps({
        "status": "passed",
        "is_valid": True,
        "overall_score": 0.96,
        "coverage": {
            "coverage_score": 0.98,
            "covered_topics": ["Topic 1", "Topic 2"],
            "missing_topics": []
        },
        "faithfulness_warnings": [],
        "notes": ["All validation checks passed successfully."]
    })

    res = ValidationResult.model_validate_json(json_str)
    assert res.status == ValidationStatus.PASSED
    assert res.is_valid is True
    assert res.coverage.coverage_score == 0.98
    assert len(res.faithfulness_warnings) == 0
