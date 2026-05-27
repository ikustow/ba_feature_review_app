from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from feature_review.openapi.schema_resolver import collect_schema_names, collect_schema_refs


HTTP_METHODS = {"get", "put", "post", "delete", "patch", "options", "head", "trace"}


class OpenAPIOperationIndexError(ValueError):
    """Raised when OpenAPI operations cannot be indexed consistently."""


@dataclass(frozen=True)
class OpenAPIOperationRecord:
    operation_id: str
    method: str
    path: str
    operation: dict[str, Any]
    path_parameters: list[dict[str, Any]]
    schema_refs: frozenset[str]
    schema_names: frozenset[str]

    @property
    def method_path(self) -> tuple[str, str]:
        return (self.method, self.path)

    @property
    def tags(self) -> tuple[str, ...]:
        return tuple(self.operation.get("tags") or [])


class OpenAPIOperationIndex:
    def __init__(self, records: list[OpenAPIOperationRecord]):
        self._records = records
        self._by_operation_id: dict[str, OpenAPIOperationRecord] = {}
        self._by_method_path: dict[tuple[str, str], OpenAPIOperationRecord] = {}
        self._by_tag: dict[str, list[OpenAPIOperationRecord]] = defaultdict(list)
        self._by_schema_name: dict[str, list[OpenAPIOperationRecord]] = defaultdict(list)

        for record in records:
            if record.operation_id in self._by_operation_id:
                raise OpenAPIOperationIndexError(f"Duplicate operationId: {record.operation_id}")
            self._by_operation_id[record.operation_id] = record
            self._by_method_path[record.method_path] = record
            for tag in record.tags:
                self._by_tag[tag].append(record)
            for schema_name in record.schema_names:
                self._by_schema_name[schema_name].append(record)

    @classmethod
    def from_spec(cls, spec: dict[str, Any]) -> "OpenAPIOperationIndex":
        records: list[OpenAPIOperationRecord] = []
        paths = spec.get("paths") or {}
        if not isinstance(paths, dict):
            raise OpenAPIOperationIndexError("OpenAPI paths must be a mapping")

        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            path_parameters = path_item.get("parameters") or []
            for method, operation in path_item.items():
                method_lower = method.lower()
                if method_lower not in HTTP_METHODS or not isinstance(operation, dict):
                    continue

                operation_id = operation.get("operationId")
                if not isinstance(operation_id, str) or not operation_id:
                    raise OpenAPIOperationIndexError(f"Operation {method_upper(method_lower)} {path} is missing operationId")

                schema_refs = collect_schema_refs(operation)
                records.append(
                    OpenAPIOperationRecord(
                        operation_id=operation_id,
                        method=method_upper(method_lower),
                        path=path,
                        operation=operation,
                        path_parameters=list(path_parameters),
                        schema_refs=frozenset(schema_refs),
                        schema_names=frozenset(collect_schema_names(operation)),
                    )
                )

        return cls(records)

    @property
    def records(self) -> list[OpenAPIOperationRecord]:
        return list(self._records)

    @property
    def operation_ids(self) -> list[str]:
        return [record.operation_id for record in self._records]

    def get(self, operation_id: str) -> OpenAPIOperationRecord:
        try:
            return self._by_operation_id[operation_id]
        except KeyError as exc:
            raise OpenAPIOperationIndexError(f"Unknown OpenAPI operationId: {operation_id}") from exc

    def get_by_method_path(self, method: str, path: str) -> OpenAPIOperationRecord:
        key = (method.upper(), path)
        try:
            return self._by_method_path[key]
        except KeyError as exc:
            raise OpenAPIOperationIndexError(f"Unknown OpenAPI operation: {method.upper()} {path}") from exc

    def by_tag(self, tag: str) -> list[OpenAPIOperationRecord]:
        return list(self._by_tag.get(tag, []))

    def by_schema_name(self, schema_name: str) -> list[OpenAPIOperationRecord]:
        return list(self._by_schema_name.get(schema_name, []))


def method_upper(method: str) -> str:
    return method.upper()
