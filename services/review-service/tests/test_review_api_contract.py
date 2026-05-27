from fastapi.testclient import TestClient

from feature_review.api.main import app


client = TestClient(app)


def test_health_returns_dataset_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["dataset_id"] == "petstore_synthetic_product_docs_v1"


def test_features_returns_four_feature_summaries():
    response = client.get("/features")

    assert response.status_code == 200
    features = response.json()["features"]
    assert [feature["title"] for feature in features] == [
        "Pet Lifecycle Management",
        "Store Order Checkout",
        "User Account Access",
        "Pet Image Upload",
    ]
    assert all(feature["diagram_count"] == 1 for feature in features)


def test_feature_context_returns_docs_openapi_slice_and_diagram():
    response = client.get("/features/us_pet_lifecycle_management_v1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["feature_id"] == "us_pet_lifecycle_management_v1"
    assert payload["acceptance_criteria"]["document_id"] == "ac_pet_lifecycle_management_v1"
    assert [operation["operation_id"] for operation in payload["openapi_operations"]] == [
        "addPet",
        "updatePet",
        "getPetById",
        "findPetsByStatus",
        "deletePet",
    ]
    assert payload["diagrams"][0]["source"].startswith("@startuml")
    assert payload["diagrams"][0]["rendered_svg"].lstrip().startswith("<svg")


def test_feature_diagrams_and_diagram_by_id_return_rendered_svg():
    list_response = client.get("/features/us_store_order_checkout_v1/diagrams")
    assert list_response.status_code == 200
    diagram_id = list_response.json()["diagrams"][0]["diagram_id"]

    diagram_response = client.get(f"/diagrams/{diagram_id}")

    assert diagram_response.status_code == 200
    assert diagram_response.json()["diagram_id"] == "diag_store_order_checkout_sequence_v1"
    assert diagram_response.json()["rendered_svg"].lstrip().startswith("<svg")


def test_openapi_operation_endpoint_returns_single_operation_slice():
    response = client.get("/openapi/operations/findPetsByStatus")

    assert response.status_code == 200
    payload = response.json()
    assert payload["operation_id"] == "findPetsByStatus"
    assert payload["method"] == "GET"
    assert payload["path"] == "/pet/findByStatus"
    assert "components" not in payload


def test_feature_audit_returns_deterministic_findings():
    response = client.post("/features/us_user_account_access_v1/audit")

    assert response.status_code == 200
    payload = response.json()
    assert payload["overall_status"] == "warnings"
    assert any(
        finding["title"] == "Login header contract needs explicit regression coverage"
        for finding in payload["findings"]
    )


def test_diagram_audit_returns_diagram_scoped_result():
    response = client.post("/features/us_pet_lifecycle_management_v1/diagram-audit")

    assert response.status_code == 200
    payload = response.json()
    assert payload["feature_id"] == "us_pet_lifecycle_management_v1"
    assert payload["overall_status"] == "passed"
    assert payload["findings"] == []
    assert payload["generated_test_ideas"] == []


def test_incident_impact_returns_related_feature_findings_and_test_ideas():
    response = client.post("/incidents/inc_pet_status_filter_mismatch_v1/impact")

    assert response.status_code == 200
    payload = response.json()
    assert payload["incident_id"] == "inc_pet_status_filter_mismatch_v1"
    assert payload["related_feature_ids"] == ["us_pet_lifecycle_management_v1"]
    assert payload["generated_test_ideas"][0]["type"] == "regression"


def test_test_gap_report_returns_generated_test_ideas():
    response = client.post("/features/us_store_order_checkout_v1/test-gaps")

    assert response.status_code == 200
    payload = response.json()
    assert payload["feature_id"] == "us_store_order_checkout_v1"
    assert any(test_idea["type"] == "boundary" for test_idea in payload["generated_test_ideas"])


def test_unknown_resource_returns_404():
    response = client.get("/features/unknown_feature")

    assert response.status_code == 404
