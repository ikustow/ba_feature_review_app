from __future__ import annotations

import html
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from feature_review.models import DiagramStep


class PlantUMLRenderError(ValueError):
    """Raised when PlantUML rendering fails and no fallback can be produced."""


FALLBACK_RENDERER_VERSION = "feature-review-fallback-v2"

_PARTICIPANT_RE = re.compile(
    r"^\s*(actor|participant|database|collections|queue|entity|boundary|control)\s+(.+?)\s*$",
    re.IGNORECASE,
)
_MESSAGE_RE = re.compile(
    r"^\s*([A-Za-z0-9_.$]+)\s+([-ox.=]+[>x]?)\s+([A-Za-z0-9_.$]+)\s*:?\s*(.*?)\s*$"
)
_OPERATION_MARKER_RE = re.compile(r"^\s*'\s*operationId:\s*([A-Za-z0-9_.-]+)\s*$")


@dataclass(frozen=True)
class _Lane:
    alias: str
    label: str
    kind: str


@dataclass(frozen=True)
class _Message:
    sender: str
    receiver: str
    label: str
    operation_id: str | None
    related_path: str | None
    dashed: bool


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
            _save_cached_svg(cache_path, rendered)
            return rendered

    rendered = _fallback_svg(source=source, title=title, steps=steps)
    _save_cached_svg(cache_path, rendered)
    return rendered


def _load_cached_svg(cache_path: Path | str | None) -> str | None:
    if cache_path is None:
        return None

    svg_path = Path(cache_path)
    if not svg_path.exists():
        return None

    svg = svg_path.read_text(encoding="utf-8")
    if "Fallback SVG rendering of PlantUML sequence steps" in svg:
        return None
    return svg if svg.lstrip().startswith("<svg") else None


def _save_cached_svg(cache_path: Path | str | None, svg: str) -> None:
    if cache_path is None:
        return

    svg_path = Path(cache_path)
    try:
        svg_path.parent.mkdir(parents=True, exist_ok=True)
        svg_path.write_text(svg, encoding="utf-8")
    except OSError:
        return


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


def _fallback_svg(*, source: str, title: str, steps: list[DiagramStep]) -> str:
    lanes, messages = _parse_sequence_for_fallback(source, steps)
    if not lanes:
        lanes = [_Lane(alias="Feature", label="Feature", kind="participant")]
    if not messages:
        messages = [
            _Message(
                sender=lanes[0].alias,
                receiver=lanes[min(1, len(lanes) - 1)].alias,
                label=step.label,
                operation_id=step.related_operation_id,
                related_path=step.related_path,
                dashed=False,
            )
            for step in steps
        ]

    width = max(920, 160 + (len(lanes) - 1) * 180)
    margin_x = 76
    top_y = 104
    lifeline_top = 132
    row_height = 66
    message_start_y = 168
    bottom_padding = 78
    height = max(260, message_start_y + row_height * len(messages) + bottom_padding)
    title_text = html.escape(title)
    lane_gap = (width - margin_x * 2) / max(1, len(lanes) - 1)
    lane_x = {lane.alias: round(margin_x + index * lane_gap, 1) for index, lane in enumerate(lanes)}

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{title_text}" '
        f'data-renderer="{FALLBACK_RENDERER_VERSION}">',
        "<defs>",
        '<marker id="arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">',
        '<path d="M0,0 L10,4 L0,8 z" fill="#2f7f7b"/>',
        "</marker>",
        '<marker id="arrow-muted" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">',
        '<path d="M0,0 L10,4 L0,8 z" fill="#64758a"/>',
        "</marker>",
        "</defs>",
        "<style>",
        ".bg{fill:#fff}.grid{stroke:#eef3f7;stroke-width:1}.title{font:700 22px Arial,sans-serif;fill:#172033}",
        ".subtitle{font:13px Arial,sans-serif;fill:#64758a}.lane{stroke:#aab7c6;stroke-width:1.5;stroke-dasharray:6 7}",
        ".box{fill:#fff;stroke:#ccd7e2;stroke-width:1.4}.box.actor{fill:#e8f4f2;stroke:#2f7f7b}",
        ".box.database{fill:#fff7e3;stroke:#d49b26}.box.collections{fill:#e8f1ff;stroke:#5282bd}",
        ".box-label{font:700 12px Arial,sans-serif;fill:#172033}.msg{stroke:#2f7f7b;stroke-width:2.2}",
        ".msg.dashed{stroke:#64758a;stroke-dasharray:7 5}.msg-label{font:700 13px Arial,sans-serif;fill:#172033}",
        ".op-chip{fill:#eef7f6;stroke:#9bd2cd;stroke-width:1}.op-text{font:700 11px Arial,sans-serif;fill:#17635e}",
        ".index{fill:#f4f7fa;stroke:#ccd7e2;stroke-width:1}.index-text{font:700 11px Arial,sans-serif;fill:#52657b}",
        "</style>",
        f'<rect class="bg" x="0" y="0" width="{width}" height="{height}"/>',
        *_grid_lines(width, height),
        f'<text x="32" y="38" class="title">{title_text}</text>',
        '<text x="32" y="60" class="subtitle">Sequence fallback rendered from PlantUML source</text>',
    ]

    for lane in lanes:
        x = lane_x[lane.alias]
        parts.extend(_participant_box(x=x, y=top_y, lane=lane))
        parts.append(f'<line x1="{x}" y1="{lifeline_top}" x2="{x}" y2="{height - 42}" class="lane"/>')

    for index, message in enumerate(messages, start=1):
        y = message_start_y + (index - 1) * row_height
        sender_x = lane_x.get(message.sender, margin_x)
        receiver_x = lane_x.get(message.receiver, width - margin_x)
        parts.extend(_message_svg(index=index, message=message, y=y, sender_x=sender_x, receiver_x=receiver_x))

    return "\n".join([*parts, "</svg>"])


def _parse_sequence_for_fallback(source: str, steps: list[DiagramStep]) -> tuple[list[_Lane], list[_Message]]:
    lanes_by_alias: dict[str, _Lane] = {}
    lane_order: list[str] = []
    messages: list[_Message] = []
    pending_operation_id: str | None = None

    for line in source.splitlines():
        participant_match = _PARTICIPANT_RE.match(line)
        if participant_match:
            kind, rest = participant_match.groups()
            label, alias = _split_participant_alias(rest)
            if alias not in lanes_by_alias:
                lanes_by_alias[alias] = _Lane(alias=alias, label=label, kind=kind.lower())
                lane_order.append(alias)
            continue

        marker_match = _OPERATION_MARKER_RE.match(line)
        if marker_match:
            pending_operation_id = marker_match.group(1).strip()
            continue

        message_match = _MESSAGE_RE.match(line)
        if not message_match:
            continue

        sender, arrow, receiver, raw_label = message_match.groups()
        for alias in (sender, receiver):
            if alias not in lanes_by_alias:
                lanes_by_alias[alias] = _Lane(alias=alias, label=alias, kind="participant")
                lane_order.append(alias)

        step = steps[len(messages)] if len(messages) < len(steps) else None
        messages.append(
            _Message(
                sender=sender,
                receiver=receiver,
                label=(step.label if step else raw_label.strip()) or f"{sender} -> {receiver}",
                operation_id=step.related_operation_id if step else pending_operation_id,
                related_path=step.related_path if step else None,
                dashed="--" in arrow or "." in arrow,
            )
        )
        pending_operation_id = None

    return [lanes_by_alias[alias] for alias in lane_order], messages


def _split_participant_alias(rest: str) -> tuple[str, str]:
    if " as " in rest:
        raw_label, alias = re.split(r"\s+as\s+", rest, maxsplit=1, flags=re.IGNORECASE)
        return raw_label.strip().strip('"'), alias.strip()
    value = rest.strip().strip('"')
    return value, value


def _grid_lines(width: int, height: int) -> list[str]:
    lines: list[str] = []
    for x in range(0, width + 1, 24):
        lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" class="grid"/>')
    for y in range(0, height + 1, 24):
        lines.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" class="grid"/>')
    return lines


def _participant_box(*, x: float, y: int, lane: _Lane) -> list[str]:
    width = min(150, max(96, len(lane.label) * 7 + 24))
    label_lines = _wrap_text(lane.label, 17)[:2]
    box_height = 36 if len(label_lines) == 1 else 50
    box_x = round(x - width / 2, 1)
    box_y = y - box_height // 2
    lines = [f'<rect x="{box_x}" y="{box_y}" width="{width}" height="{box_height}" rx="8" class="box {lane.kind}"/>']
    first_y = y + (4 if len(label_lines) == 1 else -3)
    for index, label_line in enumerate(label_lines):
        lines.append(
            f'<text x="{x}" y="{first_y + index * 14}" text-anchor="middle" '
            f'class="box-label">{html.escape(label_line)}</text>'
        )
    return lines


def _message_svg(*, index: int, message: _Message, y: int, sender_x: float, receiver_x: float) -> list[str]:
    label = message.label
    if message.operation_id:
        label = f"{label}"
    label_lines = _wrap_text(label, 34)[:2]
    center_x = round((sender_x + receiver_x) / 2, 1)
    line_class = "msg dashed" if message.dashed else "msg"
    marker = "arrow-muted" if message.dashed else "arrow"
    chip_text = message.operation_id or ""
    if chip_text and message.related_path:
        chip_text = f"{chip_text}  {message.related_path}"
    chip_width = min(260, max(86, len(chip_text) * 6 + 22)) if chip_text else 0
    chip_x = round(center_x - chip_width / 2, 1)
    label_y = y - 13 - (len(label_lines) - 1) * 7

    lines = [
        f'<circle cx="32" cy="{y}" r="12" class="index"/>',
        f'<text x="32" y="{y + 4}" text-anchor="middle" class="index-text">{index}</text>',
    ]
    for line_index, label_line in enumerate(label_lines):
        lines.append(
            f'<text x="{center_x}" y="{label_y + line_index * 14}" text-anchor="middle" '
            f'class="msg-label">{html.escape(label_line)}</text>'
        )
    lines.append(
        f'<line x1="{sender_x}" y1="{y}" x2="{receiver_x}" y2="{y}" '
        f'class="{line_class}" marker-end="url(#{marker})"/>'
    )
    if chip_text:
        lines.extend(
            [
                f'<rect x="{chip_x}" y="{y + 9}" width="{chip_width}" height="22" rx="11" class="op-chip"/>',
                f'<text x="{center_x}" y="{y + 24}" text-anchor="middle" class="op-text">{html.escape(chip_text)}</text>',
            ]
        )
    return lines


def _wrap_text(value: str, max_chars: int) -> list[str]:
    words = value.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        if len(current) + 1 + len(word) <= max_chars:
            current = f"{current} {word}"
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines
