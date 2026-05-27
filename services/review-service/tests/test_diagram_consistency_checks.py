from feature_review.checks.diagram_branch_coverage import check_diagram_only_behavior
from feature_review.checks.diagram_operation_coverage import (
    check_diagram_incident_coverage,
    check_diagram_operation_coverage,
)
from feature_review.data.feature_catalog import FeatureCatalog
from feature_review.models import DiagramStep


def test_pet_lifecycle_diagram_contains_markers_for_key_operations():
    context = FeatureCatalog.from_raw_data().get_feature_context("us_pet_lifecycle_management_v1")

    marker_operations = {
        step.related_operation_id
        for diagram in context.diagrams
        for step in diagram.steps
        if step.related_operation_id
    }

    assert marker_operations == set(context.user_story.related_openapi_operations)
    assert check_diagram_operation_coverage(context) == []
    assert check_diagram_incident_coverage(context) == []


def test_diagram_operation_coverage_reports_missing_marker():
    context = FeatureCatalog.from_raw_data().get_feature_context("us_pet_lifecycle_management_v1")
    diagram = context.diagrams[0]
    reduced_steps = [step for step in diagram.steps if step.related_operation_id != "deletePet"]
    reduced_diagram = diagram.model_copy(update={"steps": reduced_steps})
    reduced_context = context.model_copy(update={"diagrams": [reduced_diagram]})

    findings = check_diagram_operation_coverage(reduced_context)

    assert len(findings) == 1
    assert findings[0].category == "diagram_operation_coverage"
    assert findings[0].affected_operation_ids == ["deletePet"]


def test_diagram_only_behavior_reports_unlinked_operation_marker():
    context = FeatureCatalog.from_raw_data().get_feature_context("us_pet_image_upload_v1")
    diagram = context.diagrams[0]
    unexpected_step = DiagramStep(
        step_id="step_extra",
        label="GET /pet/findByTags",
        source_line=99,
        related_operation_id="findPetsByTags",
        related_path="/pet/findByTags",
    )
    mutated_diagram = diagram.model_copy(update={"steps": [*diagram.steps, unexpected_step]})
    mutated_context = context.model_copy(update={"diagrams": [mutated_diagram]})

    findings = check_diagram_only_behavior(mutated_context)

    assert len(findings) == 1
    assert findings[0].category == "diagram_branch_coverage"
    assert findings[0].affected_operation_ids == ["findPetsByTags"]
