from __future__ import annotations

from feature_review.checks.common import document_refs, docs_text, make_finding
from feature_review.models import FeatureContext, RuleFinding


def check_schema_required_fields(context: FeatureContext) -> list[RuleFinding]:
    text = docs_text(context)
    missing: list[str] = []

    for schema_entry in context.related_schemas:
        schema_name = schema_entry.get("schema_name")
        schema = schema_entry.get("schema") or {}
        required_fields = schema.get("required") or []
        for field_name in required_fields:
            candidates = [str(field_name), f"{schema_name}.{field_name}"]
            if not any(candidate.lower() in text for candidate in candidates):
                missing.append(f"{schema_name}.{field_name}")

    if not missing:
        return []

    return [
        make_finding(
            context,
            category="schema_required_fields",
            severity="medium",
            title="Required schema fields are missing from docs",
            description=(
                "The OpenAPI schemas contain required fields that are not mentioned "
                f"in story or AC text: {', '.join(missing)}."
            ),
            evidence_refs=[*document_refs(context), *(f"schema:{field}" for field in missing)],
            affected_operation_ids=context.user_story.related_openapi_operations,
            recommended_action="Mention required schema fields in product rules or acceptance criteria.",
        )
    ]
