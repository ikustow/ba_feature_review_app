from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from feature_review.data.paths import manifest_path as default_manifest_path
from feature_review.models import DatasetManifest


class ManifestLoadError(ValueError):
    """Raised when the dataset manifest is missing or structurally invalid."""


def load_manifest(path: Path | str | None = None) -> DatasetManifest:
    manifest_file = Path(path) if path is not None else default_manifest_path()
    if not manifest_file.exists():
        raise ManifestLoadError(f"Manifest file does not exist: {manifest_file}")

    try:
        payload = json.loads(manifest_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ManifestLoadError(f"Manifest contains invalid JSON: {manifest_file}") from exc

    try:
        manifest = DatasetManifest.model_validate({**payload, "path": manifest_file})
    except ValidationError as exc:
        raise ManifestLoadError(f"Manifest schema validation failed: {manifest_file}") from exc

    _validate_unique_artifact_ids(manifest)
    return manifest


def _validate_unique_artifact_ids(manifest: DatasetManifest) -> None:
    seen: set[str] = set()
    duplicates: list[str] = []
    for entry in manifest.documents:
        artifact_id = entry.artifact_id
        if artifact_id in seen:
            duplicates.append(artifact_id)
        seen.add(artifact_id)

    if duplicates:
        duplicate_list = ", ".join(sorted(duplicates))
        raise ManifestLoadError(f"Manifest contains duplicate artifact ids: {duplicate_list}")
