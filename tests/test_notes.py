from backend.domain.notes_schema import Definition, Notes, QualityMetadata, RevisionQuestion, Topic


def test_notes_basic_instantiation():
    notes = Notes(
        title="Sample Lecture Notes",
        subject="Biology",
        overview="Overview of cellular biology",
        topics=[
            Topic(
                heading="Cell Structure",
                key_points=["Cell membrane", "Nucleus", "Mitochondria"],
                definitions=[
                    Definition(term="Mitochondria", meaning="Powerhouse of the cell.")
                ]
            )
        ],
        revision_questions=[
            RevisionQuestion(
                question="What is the function of mitochondria?",
                answer="Produces cellular energy (ATP)."
            )
        ],
        quality_metadata=QualityMetadata(coverage_score=1.0)
    )
    assert notes.title == "Sample Lecture Notes"
    assert len(notes.topics) == 1
    assert notes.topics[0].heading == "Cell Structure"
    assert notes.quality_metadata.coverage_score == 1.0