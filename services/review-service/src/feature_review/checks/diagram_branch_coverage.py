from __future__ import annotations

from feature_review.checks.common import make_finding
from feature_review.models import FeatureContext, RuleFinding


def check_diagram_only_behavior(context: FeatureContext) -> list[RuleFinding]:
    allowed_operations = set(context.user_story.related_openapi_operations)
    unexpected: dict[str, list[str]] = {}

    for diagram in context.diagrams:
        diagram_operations = [
            step.related_operation_id
            for step in diagram.steps
            if step.related_operation_id and step.related_operation_id not in allowed_operations
        ]
        if diagram_operations:
            unexpected[diagram.diagram_id] = diagram_operations

    if not unexpected:
        return []

    affected = [operation_id for operations in unexpected.values() for operation_id in operations]
    return [
        make_finding(
            context,
            category="diagram_branch_coverage",
            severity="medium",
            title="Diagram describes operations outside the feature",
            description=(
                "The feature diagram contains operation markers that are not linked to "
                f"the feature manifest: {unexpected}."
            ),
            evidence_refs=[*(f"diagram:{diagram_id}" for diagram_id in unexpected)],
            affected_operation_ids=affected,
            recommended_action="Update the manifest traceability or remove unrelated behavior from the feature diagram.",
        )
    ]
