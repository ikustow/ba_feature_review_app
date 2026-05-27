from feature_review.data.feature_catalog import FeatureCatalog
from feature_review.openapi.parser import load_openapi_spec
from feature_review.openapi.slicer import OpenAPISlicer


def test_slicer_returns_only_feature_related_operations_in_manifest_order():
    slicer = OpenAPISlicer(load_openapi_spec())

    operations = slicer.slice_operations(
        ["addPet", "updatePet", "getPetById", "findPetsByStatus", "deletePet"]
    )

    assert [(operation.method, operation.path, operation.operation_id) for operation in operations] == [
        ("POST", "/pet", "addPet"),
        ("PUT", "/pet", "updatePet"),
        ("GET", "/pet/{petId}", "getPetById"),
        ("GET", "/pet/findByStatus", "findPetsByStatus"),
        ("DELETE", "/pet/{petId}", "deletePet"),
    ]
    assert "findPetsByTags" not in {operation.operation_id for operation in operations}
    assert "uploadFile" not in {operation.operation_id for operation in operations}


def test_sliced_operation_contains_compact_contract_fields():
    slicer = OpenAPISlicer(load_openapi_spec())

    operation = slicer.slice_operations(["findPetsByStatus"])[0]
    parameter = operation.parameters[0]

    assert operation.summary == "Finds Pets by status."
    assert operation.request_body is None
    assert set(operation.responses) == {"200", "400", "default"}
    assert operation.security == [{"petstore_auth": ["write:pets", "read:pets"]}]
    assert operation.tags == ["pet"]
    assert parameter["name"] == "status"
    assert parameter["schema"]["enum"] == ["available", "pending", "sold"]
    assert "components" not in operation.model_dump()


def test_slicer_returns_only_reachable_schemas_for_selected_operations():
    slicer = OpenAPISlicer(load_openapi_spec())

    schemas = slicer.related_schemas_for_operations(
        ["addPet", "updatePet", "getPetById", "findPetsByStatus", "deletePet"]
    )
    schema_names = {schema["schema_name"] for schema in schemas}

    assert schema_names == {"Pet", "Category", "Tag", "Error"}
    assert {"Order", "User", "ApiResponse"}.isdisjoint(schema_names)


def test_schema_depth_limit_controls_nested_ref_expansion():
    slicer = OpenAPISlicer(load_openapi_spec(), schema_depth_limit=0)

    schema_names = slicer.related_schema_names_for_operations(["updatePet"])

    assert set(schema_names) == {"Pet", "Error"}
    assert "Category" not in schema_names
    assert "Tag" not in schema_names


def test_feature_context_includes_openapi_slice_and_related_schemas():
    catalog = FeatureCatalog.from_raw_data()

    context = catalog.get_feature_context("us_store_order_checkout_v1")

    assert [operation.operation_id for operation in context.openapi_operations] == [
        "placeOrder",
        "getOrderById",
        "deleteOrder",
        "getInventory",
    ]
    assert {schema["schema_name"] for schema in context.related_schemas} == {"Order", "Error"}
