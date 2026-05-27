from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from feature_review.models import ManifestEntry, ProductDoc


class MarkdownLoadError(ValueError):
    """Raised when a product markdown artifact cannot be parsed."""


_TITLE_PATTERN = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def load_product_doc(path: Path | str, manifest_entry: ManifestEntry | None = None) -> ProductDoc:
    markdown_path = Path(path)
    if not markdown_path.exists():
        raise MarkdownLoadError(f"Markdown document does not exist: {markdown_path}")

    source = markdown_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(source, markdown_path)
    title = extract_title(body)

    if manifest_entry is not None:
        frontmatter = _merge_manifest_metadata(frontmatter, manifest_entry)

    try:
        return ProductDoc(
            document_id=_required_string(frontmatter, "document_id", markdown_path),
            artifact_type=_required_string(frontmatter, "artifact_type", markdown_path),
            title=title,
            domain=_required_string(frontmatter, "domain", markdown_path),
            status=str(frontmatter.get("status", "unknown")),
            version=str(frontmatter.get("version", "unknown")),
            text=body.strip(),
            frontmatter=frontmatter,
            related_openapi_operations=list(frontmatter.get("related_openapi_operations") or []),
            path=manifest_entry.path if manifest_entry else str(markdown_path),
            related_user_story=frontmatter.get("related_user_story"),
            related_diagrams=list(frontmatter.get("related_diagrams") or []),
        )
    except ValueError as exc:
        raise MarkdownLoadError(f"Invalid markdown metadata in {markdown_path}") from exc


def parse_frontmatter(source: str, path: Path | str = "<markdown>") -> tuple[dict[str, Any], str]:
    if not source.startswith("---\n"):
        raise MarkdownLoadError(f"Markdown document is missing YAML frontmatter: {path}")

    end_marker = source.find("\n---", 4)
    if end_marker == -1:
        raise MarkdownLoadError(f"Markdown document has unterminated YAML frontmatter: {path}")

    frontmatter_source = source[4:end_marker]
    body = source[end_marker + len("\n---") :].lstrip("\n")

    loaded = yaml.safe_load(frontmatter_source) or {}
    if not isinstance(loaded, dict):
        raise MarkdownLoadError(f"YAML frontmatter must be a mapping: {path}")

    return loaded, body


def extract_title(markdown_body: str) -> str:
    match = _TITLE_PATTERN.search(markdown_body)
    if not match:
        raise MarkdownLoadError("Markdown document does not contain an H1 title")
    return match.group(1).strip()


def _merge_manifest_metadata(frontmatter: dict[str, Any], manifest_entry: ManifestEntry) -> dict[str, Any]:
    merged = dict(frontmatter)
    if manifest_entry.document_id:
        merged.setdefault("document_id", manifest_entry.document_id)
    merged.setdefault("artifact_type", manifest_entry.artifact_type)
    merged.setdefault("domain", manifest_entry.domain)
    if manifest_entry.related_user_story:
        merged.setdefault("related_user_story", manifest_entry.related_user_story)
    if manifest_entry.related_openapi_operations:
        merged.setdefault("related_openapi_operations", manifest_entry.related_openapi_operations)
    if manifest_entry.related_diagrams:
        merged["related_diagrams"] = manifest_entry.related_diagrams
    return merged


def _required_string(frontmatter: dict[str, Any], key: str, path: Path) -> str:
    value = frontmatter.get(key)
    if not isinstance(value, str) or not value:
        raise MarkdownLoadError(f"Required frontmatter key {key!r} is missing in {path}")
    return value
