from __future__ import annotations

import re
from collections.abc import Iterable

from feature_review.models import FeatureContext, RuleFinding


def make_finding(
    context: FeatureContext,
    *,
    category: str,
    title: str,
    description: str,
    severity: str = "medium",
    evidence_refs: Iterable[str] = (),
    affected_operation_ids: Iterable[str] = (),
    recommended_action: str,
) -> RuleFinding:
    finding_id = f"{context.feature_id}:{category}:{slugify(title)}"
    return RuleFinding(
        finding_id=finding_id,
        severity=severity,
        category=category,
        title=title,
        description=description,
        evidence_refs=list(dict.fromkeys(evidence_refs)),
        affected_operation_ids=list(dict.fromkeys(affected_operation_ids)),
        recommended_action=recommended_action,
    )


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "finding"


def docs_text(context: FeatureContext, *, include_incidents: bool = False) -> str:
    documents = [context.user_story]
    if context.acceptance_criteria:
        documents.append(context.acceptance_criteria)
    if include_incidents:
        documents.extend(context.incidents)
    return "\n\n".join(doc.text for doc in documents).lower()


def document_refs(context: FeatureContext, *, include_incidents: bool = False) -> list[str]:
    refs = [f"doc:{context.user_story.document_id}"]
    if context.acceptance_criteria:
        refs.append(f"doc:{context.acceptance_criteria.document_id}")
    if include_incidents:
        refs.extend(f"doc:{incident.document_id}" for incident in context.incidents)
    return refs


def operation_path_map(context: FeatureContext) -> dict[str, str]:
    return {operation.operation_id: operation.path for operation in context.openapi_operations}


def contains_any(text: str, terms: Iterable[str]) -> bool:
    normalized = text.lower()
    return any(term.lower() in normalized for term in terms)
