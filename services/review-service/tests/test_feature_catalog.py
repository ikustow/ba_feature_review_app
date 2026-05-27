from feature_review.data.feature_catalog import FeatureCatalog


def test_catalog_returns_four_feature_summaries():
    catalog = FeatureCatalog.from_raw_data()

    features = catalog.list_features()

    assert [feature.title for feature in features] == [
        "Pet Lifecycle Management",
        "Store Order Checkout",
        "User Account Access",
        "Pet Image Upload",
    ]
    assert all(feature.acceptance_criteria_id for feature in features)
    assert all(feature.diagram_count == 1 for feature in features)


def test_pet_lifecycle_context_contains_docs_diagram_operations_and_incident():
    catalog = FeatureCatalog.from_raw_data()

    context = catalog.get_feature_context("us_pet_lifecycle_management_v1")

    assert context.title == "Pet Lifecycle Management"
    assert context.user_story.document_id == "us_pet_lifecycle_management_v1"
    assert context.acceptance_criteria.document_id == "ac_pet_lifecycle_management_v1"
    assert [incident.document_id for incident in context.incidents] == [
        "inc_pet_status_filter_mismatch_v1"
    ]
    assert [diagram.diagram_id for diagram in context.diagrams] == [
        "diag_pet_lifecycle_sequence_v1"
    ]
    assert context.diagrams[0].related_operation_ids == [
        "addPet",
        "updatePet",
        "getPetById",
        "findPetsByStatus",
        "deletePet",
    ]


def test_store_and_user_contexts_link_their_incidents():
    catalog = FeatureCatalog.from_raw_data()

    store_context = catalog.get_feature_context("us_store_order_checkout_v1")
    user_context = catalog.get_feature_context("us_user_account_access_v1")

    assert [incident.document_id for incident in store_context.incidents] == [
        "inc_order_id_boundary_confusion_v1"
    ]
    assert [incident.document_id for incident in user_context.incidents] == [
        "inc_login_header_contract_regression_v1"
    ]


def test_pet_image_upload_has_diagram_and_no_direct_incident_in_v1():
    catalog = FeatureCatalog.from_raw_data()

    context = catalog.get_feature_context("us_pet_image_upload_v1")

    assert [diagram.diagram_id for diagram in context.diagrams] == [
        "diag_pet_image_upload_sequence_v1"
    ]
    assert context.incidents == []
