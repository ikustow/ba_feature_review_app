from __future__ import annotations

from feature_review.checks.common import document_refs, make_finding
from feature_review.models import FeatureContext, RuleFinding


def check_operation_coverage(context: FeatureContext) -> list[RuleFinding]:
    expected = context.user_story.related_openapi_operations
    actual = {operation.operation_id for operation in context.openapi_operations}
    missing = [operation_id for operation_id in expected if operation_id not in actual]
    if not missing:
        return []

    return [
        make_finding(
            context,
            category="operation_coverage",
            severity="high",
            title="Manifest operations missing from OpenAPI slice",
            description=(
                "The feature manifest references OpenAPI operations that were not found "
                f"in the selected OpenAPI specification: {', '.join(missing)}."
            ),
            evidence_refs=[*document_refs(context), *(f"operation:{operation_id}" for operation_id in missing)],
            affected_operation_ids=missing,
            recommended_action="Fix the manifest operation IDs or update the OpenAPI source before review.",
        )
    ]


def check_acceptance_criteria_operation_coverage(context: FeatureContext) -> list[RuleFinding]:
    if context.acceptance_criteria is None:
        return [
            make_finding(
                context,
                category="traceability",
                severity="medium",
                title="Feature has no acceptance criteria document",
                description="The feature has a user story but no linked acceptance criteria artifact.",
                evidence_refs=document_refs(context),
                affected_operation_ids=context.user_story.related_openapi_operations,
                recommended_action="Add or link acceptance criteria through related_user_story.",
            )
        ]

    ac_operations = set(context.acceptance_criteria.related_openapi_operations)
    ac_text = context.acceptance_criteria.text
    missing = [
        operation_id
        for operation_id in context.user_story.related_openapi_operations
        if operation_id not in ac_operations and operation_id not in ac_text
    ]
    if not missing:
        return []

    return [
        make_finding(
            context,
            category="traceability",
            severity="medium",
            title="Acceptance criteria miss feature operations",
            description=(
                "The acceptance criteria do not explicitly cover every operation listed "
                f"for the user story. Missing operations: {', '.join(missing)}."
            ),
            evidence_refs=[
                f"doc:{context.user_story.document_id}",
                f"doc:{context.acceptance_criteria.document_id}",
                *(f"operation:{operation_id}" for operation_id in missing),
            ],
            affected_operation_ids=missing,
            recommended_action="Add AC scenarios or traceability metadata for the missing operations.",
        )
    ]
