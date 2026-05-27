from __future__ import annotations

from typing import Any

from feature_review.checks.common import document_refs, docs_text, make_finding
from feature_review.models import FeatureContext, RuleFinding


def check_enum_rules(context: FeatureContext) -> list[RuleFinding]:
    text = docs_text(context)
    missing_values: list[str] = []

    for schema_entry in context.related_schemas:
        schema_name = schema_entry.get("schema_name")
        schema = schema_entry.get("schema") or {}
        for path, enum_values in _enum_values(schema):
            for enum_value in enum_values:
                if str(enum_value).lower() not in text:
                    missing_values.append(f"{schema_name}.{path}={enum_value}")

    for operation in context.openapi_operations:
        for parameter in operation.parameters:
            schema = parameter.get("schema") or {}
            for enum_value in schema.get("enum") or []:
                if str(enum_value).lower() not in text:
                    missing_values.append(f"{operation.operation_id}.{parameter.get('name')}={enum_value}")

    if not missing_values:
        return []

    return [
        make_finding(
            context,
            category="enum_rules",
            severity="medium",
            title="Enum values are missing from product rules",
            description=(
                "OpenAPI enum values should be represented in story rules or AC. "
                f"Missing values: {', '.join(missing_values)}."
            ),
            evidence_refs=[*document_refs(context), *(f"enum:{value}" for value in missing_values)],
            affected_operation_ids=context.user_story.related_openapi_operations,
            recommended_action="Document all enum values in product rules or acceptance criteria.",
        )
    ]


def _enum_values(value: Any, prefix: str = "") -> list[tuple[str, list[Any]]]:
    found: list[tuple[str, list[Any]]] = []
    if isinstance(value, dict):
        enum = value.get("enum")
        if isinstance(enum, list):
            found.append((prefix.rstrip(".") or "$", enum))
        for key, child in value.items():
            if key == "enum":
                continue
            child_prefix = f"{prefix}{key}."
            found.extend(_enum_values(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_enum_values(child, f"{prefix}{index}."))
    return found
