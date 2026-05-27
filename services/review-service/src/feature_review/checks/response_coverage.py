from __future__ import annotations

from feature_review.checks.common import document_refs, docs_text, make_finding
from feature_review.models import FeatureContext, RuleFinding


ERROR_RESPONSE_CODES = {"400", "401", "403", "404", "409", "422", "default"}


def check_response_coverage(context: FeatureContext) -> list[RuleFinding]:
    text = docs_text(context)
    missing_by_operation: dict[str, list[str]] = {}

    for operation in context.openapi_operations:
        response_codes = set(operation.responses)
        error_codes = sorted(response_codes & ERROR_RESPONSE_CODES)
        missing_codes = [code for code in error_codes if code != "default" and code.lower() not in text]
        if "default" in error_codes and "unexpected error" not in text and "default" not in text:
            missing_codes.append("default")
        if missing_codes:
            missing_by_operation[operation.operation_id] = missing_codes

    if not missing_by_operation:
        return []

    affected = list(missing_by_operation)
    details = "; ".join(
        f"{operation_id}: {', '.join(codes)}" for operation_id, codes in missing_by_operation.items()
    )
    return [
        make_finding(
            context,
            category="response_coverage",
            severity="medium",
            title="Error responses need documentation coverage",
            description=f"Some OpenAPI error responses are not reflected in story or AC text: {details}.",
            evidence_refs=[
                *document_refs(context),
                *(f"operation:{operation_id}" for operation_id in affected),
            ],
            affected_operation_ids=affected,
            recommended_action="Add negative AC or test ideas for the missing OpenAPI error responses.",
        )
    ]
