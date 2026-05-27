from feature_review.openapi.operation_index import OpenAPIOperationIndex
from feature_review.openapi.parser import load_openapi_spec


def test_operation_index_finds_operations_by_operation_id_and_method_path():
    index = OpenAPIOperationIndex.from_spec(load_openapi_spec())

    assert len(index.records) == 19
    assert index.get("findPetsByStatus").method_path == ("GET", "/pet/findByStatus")
    assert index.get_by_method_path("post", "/store/order").operation_id == "placeOrder"


def test_operation_index_groups_by_tag_and_schema_refs():
    index = OpenAPIOperationIndex.from_spec(load_openapi_spec())

    pet_operation_ids = {record.operation_id for record in index.by_tag("pet")}
    pet_schema_operation_ids = {record.operation_id for record in index.by_schema_name("Pet")}

    assert "addPet" in pet_operation_ids
    assert "uploadFile" in pet_operation_ids
    assert "findPetsByTags" in pet_operation_ids
    assert {"addPet", "updatePet", "findPetsByStatus", "getPetById"}.issubset(pet_schema_operation_ids)


def test_operation_index_preserves_operation_schema_refs():
    index = OpenAPIOperationIndex.from_spec(load_openapi_spec())

    record = index.get("placeOrder")

    assert record.method == "POST"
    assert record.path == "/store/order"
    assert record.schema_names == frozenset({"Order", "Error"})
    assert "#/components/schemas/Order" in record.schema_refs
