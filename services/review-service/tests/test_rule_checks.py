from feature_review.checks import audit_feature_consistency
from feature_review.checks.operation_coverage import check_operation_coverage
from feature_review.data.feature_catalog import FeatureCatalog


def test_pet_lifecycle_audit_finds_update_then_filter_regression_gap():
    context = FeatureCatalog.from_raw_data().get_feature_context("us_pet_lifecycle_management_v1")

    audit = audit_feature_consistency(context)

    finding = _finding_by_title(audit.findings, "Incident implies missing update-then-filter regression test")
    assert finding.category == "incident_regression_coverage"
    assert finding.severity == "medium"
    assert finding.affected_operation_ids == ["updatePet", "findPetsByStatus"]
    assert "doc:inc_pet_status_filter_mismatch_v1" in finding.evidence_refs
    assert "changes Pet.status" in audit.generated_test_ideas[0].given_when_then
    assert audit.overall_status == "warnings"


def test_user_account_audit_finds_login_header_contract_gap():
    context = FeatureCatalog.from_raw_data().get_feature_context("us_user_account_access_v1")

    audit = audit_feature_consistency(context)

    finding = _finding_by_title(audit.findings, "Login header contract needs explicit regression coverage")
    assert finding.category == "incident_regression_coverage"
    assert finding.affected_operation_ids == ["loginUser", "logoutUser"]
    assert "header:X-Rate-Limit" in finding.evidence_refs
    assert any(test_idea.type == "contract" for test_idea in audit.generated_test_ideas)


def test_store_order_audit_finds_order_id_boundary_gap():
    context = FeatureCatalog.from_raw_data().get_feature_context("us_store_order_checkout_v1")

    audit = audit_feature_consistency(context)

    finding = _finding_by_title(audit.findings, "Order ID boundary rules need operation-specific tests")
    assert finding.category == "incident_regression_coverage"
    assert finding.severity == "low"
    assert finding.affected_operation_ids == ["getOrderById", "deleteOrder"]
    assert any(test_idea.type == "boundary" for test_idea in audit.generated_test_ideas)


def test_operation_coverage_reports_missing_openapi_operation():
    context = FeatureCatalog.from_raw_data().get_feature_context("us_pet_image_upload_v1")
    reduced_context = context.model_copy(update={"openapi_operations": context.openapi_operations[:-1]})

    findings = check_operation_coverage(reduced_context)

    assert len(findings) == 1
    assert findings[0].category == "operation_coverage"
    assert findings[0].severity == "high"
    assert findings[0].affected_operation_ids == ["updatePet"]


def test_all_findings_are_evidence_backed_and_actionable():
    context = FeatureCatalog.from_raw_data().get_feature_context("us_user_account_access_v1")

    audit = audit_feature_consistency(context)

    assert audit.findings
    assert all(finding.evidence_refs for finding in audit.findings)
    assert all(finding.recommended_action for finding in audit.findings)
    assert audit.recommended_next_actions


def _finding_by_title(findings, title):
    for finding in findings:
        if finding.title == title:
            return finding
    raise AssertionError(f"Finding not found: {title}")
