from pathlib import Path

import pytest

from feature_review.diagrams.plantuml_parser import parse_plantuml_sequence
from feature_review.diagrams.step_mapper import DiagramOperationMappingError, map_steps_to_operations
from feature_review.models import DiagramStep
from feature_review.openapi.operation_index import OpenAPIOperationIndex
from feature_review.openapi.parser import load_openapi_spec


DIAGRAM_ROOT = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "raw_data"
    / "synthetic_product_docs"
    / "diagrams"
)


def test_map_steps_to_operations_adds_openapi_paths_and_preserves_source_lines():
    source = (DIAGRAM_ROOT / "pet_lifecycle_sequence.puml").read_text(encoding="utf-8")
    parsed = parse_plantuml_sequence(source)
    index = OpenAPIOperationIndex.from_spec(load_openapi_spec())

    mapped_steps = map_steps_to_operations(parsed.steps, index)

    status_step = next(step for step in mapped_steps if step.related_operation_id == "findPetsByStatus")
    original_status_step = next(
        step for step in parsed.steps if step.related_operation_id == "findPetsByStatus"
    )
    assert status_step.related_path == "/pet/findByStatus"
    assert status_step.source_line == original_status_step.source_line


def test_map_steps_to_operations_rejects_unknown_operation_marker():
    index = OpenAPIOperationIndex.from_spec(load_openapi_spec())
    steps = [
        DiagramStep(
            step_id="step_1",
            label="GET /unknown",
            source_line=12,
            related_operation_id="unknownOperation",
        )
    ]

    with pytest.raises(DiagramOperationMappingError):
        map_steps_to_operations(steps, index)
