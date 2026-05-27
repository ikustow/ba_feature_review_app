from __future__ import annotations

from copy import deepcopy
from typing import Iterable

from feature_review.models import OpenAPIOperationSlice
from feature_review.openapi.operation_index import OpenAPIOperationIndex, OpenAPIOperationRecord
from feature_review.openapi.schema_resolver import resolve_schema_names, resolve_schemas


class OpenAPISliceError(ValueError):
    """Raised when a requested OpenAPI slice cannot be produced."""


class OpenAPISlicer:
    def __init__(
        self,
        spec: dict,
        index: OpenAPIOperationIndex | None = None,
        *,
        schema_depth_limit: int = 2,
    ):
        self.spec = spec
        self.index = index or OpenAPIOperationIndex.from_spec(spec)
        self.schema_depth_limit = schema_depth_limit

    def slice_operations(self, operation_ids: Iterable[str]) -> list[OpenAPIOperationSlice]:
        return [self._operation_slice(self.index.get(operation_id)) for operation_id in operation_ids]

    def related_schemas_for_operations(self, operation_ids: Iterable[str]) -> list[dict]:
        schema_names = self.related_schema_names_for_operations(operation_ids)
        resolved = resolve_schemas(self.spec, schema_names, max_depth=self.schema_depth_limit)
        return [{"schema_name": schema_name, "schema": schema} for schema_name, schema in resolved.items()]

    def related_schema_names_for_operations(self, operation_ids: Iterable[str]) -> list[str]:
        seed_names: list[str] = []
        seen: set[str] = set()
        for operation_id in operation_ids:
            record = self.index.get(operation_id)
            for schema_name in sorted(record.schema_names):
                if schema_name not in seen:
                    seen.add(schema_name)
                    seed_names.append(schema_name)

        return resolve_schema_names(self.spec, seed_names, max_depth=self.schema_depth_limit)

    def _operation_slice(self, record: OpenAPIOperationRecord) -> OpenAPIOperationSlice:
        operation = record.operation
        parameters = [*record.path_parameters, *(operation.get("parameters") or [])]
        related_schema_names = resolve_schema_names(
            self.spec,
            sorted(record.schema_names),
            max_depth=self.schema_depth_limit,
        )

        return OpenAPIOperationSlice(
            operation_id=record.operation_id,
            method=record.method,
            path=record.path,
            summary=operation.get("summary"),
            description=operation.get("description"),
            parameters=deepcopy(parameters),
            request_body=deepcopy(operation.get("requestBody")),
            responses=deepcopy(operation.get("responses") or {}),
            security=deepcopy(operation.get("security") or []),
            tags=list(operation.get("tags") or []),
            related_schema_names=related_schema_names,
        )
