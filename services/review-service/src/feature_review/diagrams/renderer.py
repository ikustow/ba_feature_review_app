from __future__ import annotations

import html
import shutil
import subprocess
from pathlib import Path

from feature_review.models import DiagramStep


class PlantUMLRenderError(ValueError):
    """Raised when PlantUML rendering fails and no fallback can be produced."""


def render_plantuml_svg(
    source: str,
    *,
    title: str,
    steps: list[DiagramStep],
    cache_path: Path | str | None = None,
) -> str:
    cached_svg = _load_cached_svg(cache_path)
    if cached_svg is not None:
        return cached_svg

    plantuml_binary = shutil.which("plantuml")
    if plantuml_binary:
        rendered = _render_with_plantuml_cli(plantuml_binary, source)
        if rendered:
            return rendered

    return _fallback_svg(title=title, steps=steps)


def _load_cached_svg(cache_path: Path | str | None) -> str | None:
    if cache_path is None:
        return None

    svg_path = Path(cache_path)
    if not svg_path.exists():
        return None

    svg = svg_path.read_text(encoding="utf-8")
    return svg if svg.lstrip().startswith("<svg") else None


def _render_with_plantuml_cli(plantuml_binary: str, source: str) -> str | None:
    try:
        result = subprocess.run(
            [plantuml_binary, "-tsvg", "-pipe"],
            input=source,
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    svg = result.stdout.strip()
    if result.returncode == 0 and svg.startswith("<svg"):
        return svg
    return None


def _fallback_svg(*, title: str, steps: list[DiagramStep]) -> str:
    width = 920
    row_height = 28
    height = max(180, 96 + row_height * len(steps))
    title_text = html.escape(title)
    step_rows = []

    for index, step in enumerate(steps, start=1):
        y = 72 + index * row_height
        marker = f" [{step.related_operation_id}]" if step.related_operation_id else ""
        label = html.escape(f"{index}. {step.label}{marker}")
        step_rows.append(f'<text x="32" y="{y}" class="step">{label}</text>')

    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="{title_text}">',
            "<style>",
            ".bg{fill:#ffffff}.title{font:700 22px Arial,sans-serif;fill:#1f2937}",
            ".subtitle{font:13px Arial,sans-serif;fill:#6b7280}.step{font:14px Arial,sans-serif;fill:#111827}",
            ".rule{stroke:#d1d5db;stroke-width:1}",
            "</style>",
            f'<rect class="bg" x="0" y="0" width="{width}" height="{height}" rx="0"/>',
            f'<text x="32" y="38" class="title">{title_text}</text>',
            '<text x="32" y="60" class="subtitle">Fallback SVG rendering of PlantUML sequence steps</text>',
            '<line x1="32" y1="76" x2="888" y2="76" class="rule"/>',
            *step_rows,
            "</svg>",
        ]
    )
