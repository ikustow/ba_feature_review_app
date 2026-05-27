from __future__ import annotations

from feature_review.checks.diagram_branch_coverage import check_diagram_only_behavior
from feature_review.checks.diagram_operation_coverage import (
    check_diagram_incident_coverage,
    check_diagram_operation_coverage,
)
from feature_review.checks.enum_rules import check_enum_rules
from feature_review.checks.incident_regression import (
    check_incident_regression_coverage,
    generate_incident_regression_test_ideas,
)
from feature_review.checks.open_questions import check_open_questions
from feature_review.checks.operation_coverage import (
    check_acceptance_criteria_operation_coverage,
    check_operation_coverage,
)
from feature_review.checks.response_coverage import check_response_coverage
from feature_review.checks.schema_required_fields import check_schema_required_fields
from feature_review.checks.security_coverage import check_security_coverage
from feature_review.models import FeatureAuditResult, FeatureContext, RuleFinding, TestIdea


def audit_feature_consistency(context: FeatureContext) -> FeatureAuditResult:
    findings = _dedupe_findings(
        [
            *check_operation_coverage(context),
            *check_acceptance_criteria_operation_coverage(context),
            *check_response_coverage(context),
            *check_schema_required_fields(context),
            *check_enum_rules(context),
            *check_security_coverage(context),
            *check_diagram_operation_coverage(context),
            *check_diagram_only_behavior(context),
            *check_diagram_incident_coverage(context),
            *check_incident_regression_coverage(context),
            *check_open_questions(context),
        ]
    )
    test_ideas = generate_incident_regression_test_ideas(context)
    return FeatureAuditResult(
        review_id=f"{context.feature_id}:deterministic_audit_v1",
        feature_id=context.feature_id,
        overall_status=_overall_status(findings),
        findings=findings,
        generated_test_ideas=test_ideas,
        recommended_next_actions=_recommended_next_actions(findings, test_ideas),
        model_context_hint=(
            "Findings are deterministic rule-check outputs. Use evidence_refs and affected_operation_ids "
            "when explaining gaps; do not invent endpoints or document changes."
        ),
    )


def _overall_status(findings: list[RuleFinding]) -> str:
    severities = {finding.severity for finding in findings}
    if "high" in severities:
        return "failed"
    if findings:
        return "warnings"
    return "passed"


def _recommended_next_actions(findings: list[RuleFinding], test_ideas: list[TestIdea]) -> list[str]:
    actions = [finding.recommended_action for finding in findings if finding.severity in {"high", "medium"}]
    if test_ideas:
        actions.append("Review generated regression and contract test ideas with QA.")
    return list(dict.fromkeys(actions))


def _dedupe_findings(findings: list[RuleFinding]) -> list[RuleFinding]:
    deduped: dict[str, RuleFinding] = {}
    for finding in findings:
        deduped[finding.finding_id] = finding
    return list(deduped.values())
