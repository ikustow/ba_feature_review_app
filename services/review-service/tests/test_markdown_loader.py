from pathlib import Path

from feature_review.data.markdown_loader import load_product_doc, parse_frontmatter


PRODUCT_DOCS_ROOT = Path(__file__).resolve().parents[3] / "docs" / "raw_data" / "synthetic_product_docs"


def test_parse_frontmatter_returns_metadata_and_body():
    source = (PRODUCT_DOCS_ROOT / "user_stories" / "us_pet_lifecycle_management.md").read_text(
        encoding="utf-8"
    )

    frontmatter, body = parse_frontmatter(source)

    assert frontmatter["document_id"] == "us_pet_lifecycle_management_v1"
    assert frontmatter["artifact_type"] == "user_story"
    assert "Pet Lifecycle Management" in body


def test_load_product_doc_preserves_core_metadata_and_text():
    doc = load_product_doc(PRODUCT_DOCS_ROOT / "acceptance_criteria" / "ac_store_order_checkout.md")

    assert doc.document_id == "ac_store_order_checkout_v1"
    assert doc.artifact_type == "acceptance_criteria"
    assert doc.domain == "store"
    assert doc.version == "v1"
    assert doc.title == "Acceptance Criteria: Store Order Checkout"
    assert doc.related_user_story == "us_store_order_checkout_v1"
    assert doc.related_openapi_operations == [
        "placeOrder",
        "getOrderById",
        "deleteOrder",
        "getInventory",
    ]
    assert doc.text.startswith("# Acceptance Criteria: Store Order Checkout")
