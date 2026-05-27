from __future__ import annotations

from pathlib import Path

from feature_review.diagrams.plantuml_parser import PlantUMLParseError, parse_plantuml_sequence
from feature_review.diagrams.renderer import render_plantuml_svg
from feature_review.diagrams.step_mapper import DiagramOperationMappingError, map_steps_to_operations
from feature_review.models import FeatureDiagram, ManifestEntry
from feature_review.openapi.operation_index import OpenAPIOperationIndex


class DiagramLoadError(ValueError):
    """Raised when a diagram artifact cannot be loaded or mapped."""


class DiagramLoader:
    def __init__(
        self,
        product_docs_root: Path | str,
        *,
        operation_index: OpenAPIOperationIndex | None = None,
        svg_cache_dir: Path | str | None = None,
    ):
        self.product_docs_root = Path(product_docs_root)
        self.operation_index = operation_index
        self.svg_cache_dir = Path(svg_cache_dir) if svg_cache_dir else None

    def load_manifest_diagram(self, entry: ManifestEntry, feature_id: str) -> FeatureDiagram:
        if entry.artifact_type != "uml_diagram":
            raise DiagramLoadError(f"Manifest entry is not a diagram: {entry.artifact_id}")

        source_path = self.product_docs_root / entry.path
        if not source_path.exists():
            raise DiagramLoadError(f"Diagram source does not exist: {source_path}")

        source = source_path.read_text(encoding="utf-8")
        try:
            parsed = parse_plantuml_sequence(source)
            mapped_steps = map_steps_to_operations(parsed.steps, self.operation_index)
        except (PlantUMLParseError, DiagramOperationMappingError) as exc:
            raise DiagramLoadError(f"Failed to load diagram {entry.artifact_id}") from exc

        rendered_svg = render_plantuml_svg(
            source,
            title=parsed.title,
            steps=mapped_steps,
            cache_path=self._cache_path(entry),
        )

        return FeatureDiagram(
            diagram_id=entry.artifact_id,
            feature_id=feature_id,
            title=entry.title or parsed.title,
            diagram_type=entry.diagram_type or "sequence",
            source=source,
            rendered_svg=rendered_svg,
            related_operation_ids=entry.related_openapi_operations or parsed.related_operation_ids,
            steps=mapped_steps,
            path=entry.path,
        )

    def _cache_path(self, entry: ManifestEntry) -> Path | None:
        if self.svg_cache_dir is None:
            return None
        return self.svg_cache_dir / f"{entry.artifact_id}.svg"
