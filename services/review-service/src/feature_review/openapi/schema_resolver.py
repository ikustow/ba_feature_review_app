from __future__ import annotations

from collections import deque
from copy import deepcopy
from typing import Any, Iterable


SchemaMap = dict[str, dict[str, Any]]


SCHEMA_REF_PREFIX = "#/components/schemas/"


def collect_schema_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    _collect_schema_refs(value, refs)
    return refs


def collect_schema_names(value: Any) -> set[str]:
    return {schema_name_from_ref(ref) for ref in collect_schema_refs(value)}


def schema_name_from_ref(ref: str) -> str:
    if not ref.startswith(SCHEMA_REF_PREFIX):
        raise ValueError(f"Only local component schema refs are supported: {ref}")
    return ref.removeprefix(SCHEMA_REF_PREFIX)


def ref_from_schema_name(schema_name: str) -> str:
    return f"{SCHEMA_REF_PREFIX}{schema_name}"


def resolve_schema_names(
    spec: dict[str, Any],
    seed_schema_names: Iterable[str],
    *,
    max_depth: int = 2,
) -> list[str]:
    schemas = _component_schemas(spec)
    resolved: list[str] = []
    seen: set[str] = set()
    queue: deque[tuple[str, int]] = deque((name, 0) for name in seed_schema_names)

    while queue:
        schema_name, depth = queue.popleft()
        if schema_name in seen or schema_name not in schemas:
            continue

        seen.add(schema_name)
        resolved.append(schema_name)

        if depth >= max_depth:
            continue

        nested_refs = collect_schema_refs(schemas[schema_name])
        for nested_ref in sorted(nested_refs):
            queue.append((schema_name_from_ref(nested_ref), depth + 1))

    return resolved


def resolve_schemas(
    spec: dict[str, Any],
    seed_schema_names: Iterable[str],
    *,
    max_depth: int = 2,
) -> SchemaMap:
    schemas = _component_schemas(spec)
    resolved_names = resolve_schema_names(spec, seed_schema_names, max_depth=max_depth)
    return {schema_name: deepcopy(schemas[schema_name]) for schema_name in resolved_names}


def _collect_schema_refs(value: Any, refs: set[str]) -> None:
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str) and ref.startswith(SCHEMA_REF_PREFIX):
            refs.add(ref)
        for nested_value in value.values():
            _collect_schema_refs(nested_value, refs)
    elif isinstance(value, list):
        for item in value:
            _collect_schema_refs(item, refs)


def _component_schemas(spec: dict[str, Any]) -> dict[str, Any]:
    components = spec.get("components") or {}
    schemas = components.get("schemas") or {}
    if not isinstance(schemas, dict):
        return {}
    return schemas
