from feature_review.data.manifest_loader import load_manifest


def test_load_manifest_with_product_docs_and_diagram_entries():
    manifest = load_manifest()

    assert manifest.dataset_id == "petstore_synthetic_product_docs_v1"
    assert len(manifest.product_doc_entries) == 11
    assert len(manifest.diagram_entries) == 4
    assert manifest.counts["user_story"] == 4
    assert manifest.counts["uml_diagram"] == 4


def test_manifest_links_each_user_story_to_one_diagram():
    manifest = load_manifest()
    story_entries = [entry for entry in manifest.product_doc_entries if entry.artifact_type == "user_story"]

    assert {entry.artifact_id for entry in story_entries} == {
        "us_pet_lifecycle_management_v1",
        "us_store_order_checkout_v1",
        "us_user_account_access_v1",
        "us_pet_image_upload_v1",
    }
    assert all(len(entry.related_diagrams) == 1 for entry in story_entries)
    assert manifest.entry_by_id("diag_pet_lifecycle_sequence_v1").path == "diagrams/pet_lifecycle_sequence.puml"
