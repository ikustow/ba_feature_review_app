from __future__ import annotations

import re

from feature_review.checks.common import make_finding
from feature_review.models import FeatureContext, ProductDoc, RuleFinding


def check_open_questions(context: FeatureContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    for doc in [context.user_story, context.acceptance_criteria, *context.incidents]:
        if doc is None:
            continue
        questions = _extract_questions(doc)
        if not questions:
            continue
        findings.append(
            make_finding(
                context,
                category="open_question",
                severity="low",
                title=f"Open questions remain in {doc.document_id}",
                description="; ".join(questions),
                evidence_refs=[f"doc:{doc.document_id}"],
                affected_operation_ids=doc.related_openapi_operations,
                recommended_action="Resolve or explicitly accept these open questions before sign-off.",
            )
        )
    return findings


def _extract_questions(doc: ProductDoc) -> list[str]:
    questions: list[str] = []
    in_question_section = False
    for line in doc.text.splitlines():
        stripped = line.strip()
        if re.match(r"^##\s+(Open Questions|Follow-up Questions)", stripped, re.IGNORECASE):
            in_question_section = True
            continue
        if in_question_section and stripped.startswith("## "):
            break
        if in_question_section and stripped.startswith("- "):
            questions.append(stripped.removeprefix("- ").strip())
    return questions
