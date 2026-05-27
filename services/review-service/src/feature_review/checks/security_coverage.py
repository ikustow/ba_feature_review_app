from __future__ import annotations

from feature_review.checks.common import contains_any, document_refs, docs_text, make_finding
from feature_review.models import FeatureContext, RuleFinding


def check_security_coverage(context: FeatureContext) -> list[RuleFinding]:
    text = docs_text(context)
    missing: dict[str, list[str]] = {}

    for operation in context.openapi_operations:
        scheme_names = [scheme for requirement in operation.security for scheme in requirement]
        if not scheme_names:
            continue

        documented = any(scheme.lower() in text for scheme in scheme_names) or contains_any(
            text,
            ["auth", "authorization", "authorize", "api key", "api_key", "security"],
        )
        if not documented:
            missing[operation.operation_id] = scheme_names

    if not missing:
        return []

    return [
        make_finding(
            context,
            category="security_coverage",
            severity="medium",
            title="Secured operations need auth expectations",
            description=(
                "Some secured OpenAPI operations do not have corresponding auth or authorization "
                f"expectations in story or AC text: {missing}."
            ),
            evidence_refs=[
                *document_refs(context),
                *(f"operation:{operation_id}" for operation_id in missing),
            ],
            affected_operation_ids=list(missing),
            recommended_action="Add authorization expectations for secured operations in AC or product rules.",
        )
    ]
