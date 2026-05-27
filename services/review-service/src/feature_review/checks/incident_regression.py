from __future__ import annotations

from feature_review.checks.common import make_finding
from feature_review.models import FeatureContext, RuleFinding, TestIdea


def check_incident_regression_coverage(context: FeatureContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    for incident in context.incidents:
        if incident.document_id == "inc_pet_status_filter_mismatch_v1":
            findings.append(
                make_finding(
                    context,
                    category="incident_regression_coverage",
                    severity="medium",
                    title="Incident implies missing update-then-filter regression test",
                    description=(
                        "The incident describes stale status filtering after PUT /pet, while the AC only "
                        "checks filtering by status as a standalone scenario."
                    ),
                    evidence_refs=[
                        f"doc:{incident.document_id}",
                        f"doc:{context.acceptance_criteria.document_id}" if context.acceptance_criteria else "",
                        "operation:updatePet",
                        "operation:findPetsByStatus",
                    ],
                    affected_operation_ids=["updatePet", "findPetsByStatus"],
                    recommended_action=(
                        "Add a regression test that updates Pet.status and immediately queries "
                        "GET /pet/findByStatus."
                    ),
                )
            )
        elif incident.document_id == "inc_login_header_contract_regression_v1":
            findings.append(
                make_finding(
                    context,
                    category="incident_regression_coverage",
                    severity="medium",
                    title="Login header contract needs explicit regression coverage",
                    description=(
                        "The incident says successful login responses sometimes omitted documented "
                        "X-Rate-Limit and X-Expires-After headers."
                    ),
                    evidence_refs=[
                        f"doc:{incident.document_id}",
                        "operation:loginUser",
                        "header:X-Rate-Limit",
                        "header:X-Expires-After",
                    ],
                    affected_operation_ids=["loginUser", "logoutUser"],
                    recommended_action=(
                        "Add contract tests for successful login headers and keep logout expectations separate."
                    ),
                )
            )
        elif incident.document_id == "inc_order_id_boundary_confusion_v1":
            findings.append(
                make_finding(
                    context,
                    category="incident_regression_coverage",
                    severity="low",
                    title="Order ID boundary rules need operation-specific tests",
                    description=(
                        "The incident records inconsistent expectations between order lookup and delete "
                        "ID boundary behavior."
                    ),
                    evidence_refs=[
                        f"doc:{incident.document_id}",
                        "operation:getOrderById",
                        "operation:deleteOrder",
                    ],
                    affected_operation_ids=["getOrderById", "deleteOrder"],
                    recommended_action=(
                        "Keep lookup and delete boundary tests separate and avoid shared ambiguous IDs around 1000."
                    ),
                )
            )
    return [finding for finding in findings if all(finding.evidence_refs)]


def generate_incident_regression_test_ideas(context: FeatureContext) -> list[TestIdea]:
    ideas: list[TestIdea] = []
    for incident in context.incidents:
        if incident.document_id == "inc_pet_status_filter_mismatch_v1":
            ideas.append(
                TestIdea(
                    test_id=f"{context.feature_id}:regression:updatePet_findPetsByStatus",
                    title="Regression: update Pet.status then filter by status",
                    type="regression",
                    related_operation_ids=["updatePet", "findPetsByStatus"],
                    given_when_then=(
                        "Given an existing pet, when PUT /pet changes Pet.status and GET "
                        "/pet/findByStatus is called immediately, then only pets with the requested "
                        "status are returned."
                    ),
                    rationale="Covers the stale status index regression described by the incident.",
                )
            )
        elif incident.document_id == "inc_login_header_contract_regression_v1":
            ideas.append(
                TestIdea(
                    test_id=f"{context.feature_id}:contract:loginUser_headers",
                    title="Contract: successful login returns documented headers",
                    type="contract",
                    related_operation_ids=["loginUser"],
                    given_when_then=(
                        "Given valid login credentials, when GET /user/login succeeds, then "
                        "X-Rate-Limit and X-Expires-After response headers are present when required."
                    ),
                    rationale="Covers the login header contract regression.",
                )
            )
        elif incident.document_id == "inc_order_id_boundary_confusion_v1":
            ideas.append(
                TestIdea(
                    test_id=f"{context.feature_id}:boundary:orderId_operation_rules",
                    title="Boundary: separate lookup and delete orderId expectations",
                    type="boundary",
                    related_operation_ids=["getOrderById", "deleteOrder"],
                    given_when_then=(
                        "Given order IDs near documented boundaries, when lookup and delete are tested, "
                        "then each operation follows its own documented boundary behavior."
                    ),
                    rationale="Prevents shared regression suites from mixing operation-specific orderId rules.",
                )
            )
    return ideas
