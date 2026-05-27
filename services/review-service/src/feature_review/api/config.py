from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from feature_review.data.paths import find_repo_root


@dataclass(frozen=True)
class ReviewServiceSettings:
    raw_data_dir: Path
    openapi_path: Path
    manifest_path: Path
    diagram_svg_cache_dir: Path


def load_settings() -> ReviewServiceSettings:
    repo_root = find_repo_root()
    raw_data = _path_from_env("RAW_DATA_DIR", repo_root / "docs" / "raw_data")
    openapi_path = _path_from_env("OPENAPI_PATH", raw_data / "openapi.yaml")
    manifest_path = _path_from_env(
        "MANIFEST_PATH",
        raw_data / "synthetic_product_docs" / "manifest.json",
    )
    diagram_svg_cache_dir = _path_from_env(
        "DIAGRAM_SVG_CACHE_DIR",
        repo_root / "services" / "review-service" / ".cache" / "diagrams",
    )
    return ReviewServiceSettings(
        raw_data_dir=raw_data,
        openapi_path=openapi_path,
        manifest_path=manifest_path,
        diagram_svg_cache_dir=diagram_svg_cache_dir,
    )


def _path_from_env(name: str, default: Path) -> Path:
    value = os.getenv(name)
    return Path(value).expanduser().resolve() if value else default.resolve()
