from feature_review.data.diagram_loader import DiagramLoader
from feature_review.data.feature_catalog import FeatureCatalog
from feature_review.data.manifest_loader import load_manifest
from feature_review.data.paths import product_docs_dir
from feature_review.openapi.operation_index import OpenAPIOperationIndex
from feature_review.openapi.parser import load_openapi_spec


def test_diagram_loader_returns_source_rendered_svg_and_mapped_steps():
    manifest = load_manifest()
    entry = manifest.entry_by_id("diag_pet_lifecycle_sequence_v1")
    loader = DiagramLoader(
        product_docs_dir(),
        operation_index=OpenAPIOperationIndex.from_spec(load_openapi_spec()),
    )

    diagram = loader.load_manifest_diagram(entry, "us_pet_lifecycle_management_v1")

    assert diagram.diagram_id == "diag_pet_lifecycle_sequence_v1"
    assert diagram.source.startswith("@startuml")
    assert diagram.rendered_svg is not None
    assert diagram.rendered_svg.lstrip().startswith("<svg")
    assert diagram.related_operation_ids == [
        "addPet",
        "updatePet",
        "getPetById",
        "findPetsByStatus",
        "deletePet",
    ]

    mapped_operation_steps = [step for step in diagram.steps if step.related_operation_id]
    assert len(mapped_operation_steps) == 5
    assert mapped_operation_steps[3].related_operation_id == "findPetsByStatus"
    assert mapped_operation_steps[3].related_path == "/pet/findByStatus"


def test_feature_catalog_context_loads_one_full_diagram_for_every_feature():
    catalog = FeatureCatalog.from_raw_data()

    for feature in catalog.list_features():
        context = catalog.get_feature_context(feature.feature_id)

        assert len(context.diagrams) == 1
        diagram = context.diagrams[0]
        assert diagram.source.startswith("@startuml")
        assert diagram.rendered_svg is not None
        assert diagram.steps
        assert {step.related_operation_id for step in diagram.steps if step.related_operation_id} == set(
            context.user_story.related_openapi_operations
        )
