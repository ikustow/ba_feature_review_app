from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    current = (start or Path(__file__)).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "docs" / "raw_data" / "openapi.yaml").exists():
            return candidate
    raise FileNotFoundError("Could not locate repository root containing docs/raw_data/openapi.yaml")


def raw_data_dir(repo_root: Path | None = None) -> Path:
    return (repo_root or find_repo_root()) / "docs" / "raw_data"


def product_docs_dir(repo_root: Path | None = None) -> Path:
    return raw_data_dir(repo_root) / "synthetic_product_docs"


def manifest_path(repo_root: Path | None = None) -> Path:
    return product_docs_dir(repo_root) / "manifest.json"
