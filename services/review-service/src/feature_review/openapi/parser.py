from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from feature_review.data.paths import raw_data_dir


class OpenAPILoadError(ValueError):
    """Raised when an OpenAPI document cannot be loaded as a mapping."""


OpenAPISpec = dict[str, Any]


def default_openapi_path(repo_root: Path | str | None = None) -> Path:
    root = Path(repo_root) if repo_root is not None else None
    return raw_data_dir(root) / "openapi.yaml"


def load_openapi_spec(path: Path | str | None = None) -> OpenAPISpec:
    spec_path = Path(path) if path is not None else default_openapi_path()
    if not spec_path.exists():
        raise OpenAPILoadError(f"OpenAPI spec does not exist: {spec_path}")

    payload = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise OpenAPILoadError(f"OpenAPI spec must parse to a mapping: {spec_path}")
    if not isinstance(payload.get("paths"), dict):
        raise OpenAPILoadError(f"OpenAPI spec is missing a paths mapping: {spec_path}")

    return payload
