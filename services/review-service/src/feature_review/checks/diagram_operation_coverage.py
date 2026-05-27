from __future__ import annotations

from feature_review.checks.common import make_finding
from feature_review.models import FeatureContext, RuleFinding


def check_diagram_operation_coverage(context: FeatureContext) -> list[RuleFinding]:
    expected = set(context.user_story.related_openapi_operations)
    actual = {
        step.related_operation_id
        for diagram in context.diagrams
        for step in diagram.steps
        if step.related_operation_id
    }
    missing = sorted(expected - actual)
    if not missing:
        return []

    return [
        make_finding(
            context,
            category="diagram_operation_coverage",
            severity="medium",
            title="Feature diagram is missing operation markers",
            description=(
                "The related UML diagram does not contain operation markers for "
                f"all feature operations. Missing markers: {', '.join(missing)}."
            ),
            evidence_refs=[
                *(f"diagram:{diagram.diagram_id}" for diagram in context.diagrams),
                *(f"operation:{operation_id}" for operation_id in missing),
            ],
            affected_operation_ids=missing,
            recommended_action="Add PlantUML operationId comments near the relevant sequence steps.",
        )
    ]


def check_diagram_incident_coverage(context: FeatureContext) -> list[RuleFinding]:
    diagram_operations = {
        step.related_operation_id
        for diagram in context.diagrams
        for step in diagram.steps
        if step.related_operation_id
    }
    missing: dict[str, list[str]] = {}
    for incident in context.incidents:
        absent = [
            operation_id
            for operation_id in incident.related_openapi_operations
            if operation_id not in diagram_operations
        ]
        if absent:
            missing[incident.document_id] = absent

    if not missing:
        return []

    affected = [operation_id for operations in missing.values() for operation_id in operations]
    return [
        make_finding(
            context,
            category="diagram_operation_coverage",
            severity="medium",
            title="Incident-affected operations are missing from diagram",
            description=(
                "Some operations referenced by related incidents are not present in the feature flow: "
                f"{missing}."
            ),
            evidence_refs=[
                *(f"doc:{incident_id}" for incident_id in missing),
                *(f"diagram:{diagram.diagram_id}" for diagram in context.diagrams),
            ],
            affected_operation_ids=affected,
            recommended_action="Add incident-affected operations to the diagram or split the incident from this feature.",
        )
    ]
