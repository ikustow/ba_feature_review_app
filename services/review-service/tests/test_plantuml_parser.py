from pathlib import Path

import pytest

from feature_review.diagrams.plantuml_parser import PlantUMLParseError, parse_plantuml_sequence


DIAGRAM_ROOT = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "raw_data"
    / "synthetic_product_docs"
    / "diagrams"
)


def test_parse_plantuml_sequence_extracts_title_participants_steps_and_markers():
    source = (DIAGRAM_ROOT / "pet_lifecycle_sequence.puml").read_text(encoding="utf-8")

    parsed = parse_plantuml_sequence(source)

    assert parsed.title == "Pet Lifecycle Management Sequence"
    assert {participant.alias for participant in parsed.participants} == {
        "Manager",
        "Workspace",
        "PetAPI",
        "Catalog",
    }
    assert [step.related_operation_id for step in parsed.steps if step.related_operation_id] == [
        "addPet",
        "updatePet",
        "getPetById",
        "findPetsByStatus",
        "deletePet",
    ]

    status_step = next(step for step in parsed.steps if step.related_operation_id == "findPetsByStatus")
    assert status_step.label == "GET /pet/findByStatus"
    assert status_step.source_line is not None


def test_parse_plantuml_sequence_requires_uml_boundaries_and_title():
    with pytest.raises(PlantUMLParseError):
        parse_plantuml_sequence("title Missing boundaries")

    with pytest.raises(PlantUMLParseError):
        parse_plantuml_sequence("@startuml\nAlice -> Bob: hello\n@enduml")
