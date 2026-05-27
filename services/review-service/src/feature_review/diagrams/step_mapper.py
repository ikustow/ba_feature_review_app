from __future__ import annotations

from feature_review.models import DiagramStep
from feature_review.openapi.operation_index import OpenAPIOperationIndex, OpenAPIOperationIndexError


class DiagramOperationMappingError(ValueError):
    """Raised when a diagram operation marker cannot be mapped to OpenAPI."""


def map_steps_to_operations(
    steps: list[DiagramStep],
    operation_index: OpenAPIOperationIndex | None,
) -> list[DiagramStep]:
    if operation_index is None:
        return steps

    mapped_steps: list[DiagramStep] = []
    for step in steps:
        if not step.related_operation_id:
            mapped_steps.append(step)
            continue

        try:
            operation = operation_index.get(step.related_operation_id)
        except OpenAPIOperationIndexError as exc:
            raise DiagramOperationMappingError(
                f"Diagram step {step.step_id} references unknown operationId "
                f"{step.related_operation_id!r}"
            ) from exc

        mapped_steps.append(step.model_copy(update={"related_path": operation.path}))

    return mapped_steps
