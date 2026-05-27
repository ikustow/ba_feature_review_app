from __future__ import annotations

import re
from dataclasses import dataclass

from feature_review.models import DiagramStep


class PlantUMLParseError(ValueError):
    """Raised when a PlantUML sequence diagram cannot be parsed."""


@dataclass(frozen=True)
class PlantUMLParticipant:
    alias: str
    label: str
    kind: str
    source_line: int


@dataclass(frozen=True)
class ParsedPlantUMLDiagram:
    title: str
    diagram_type: str
    participants: list[PlantUMLParticipant]
    steps: list[DiagramStep]

    @property
    def related_operation_ids(self) -> list[str]:
        return [step.related_operation_id for step in self.steps if step.related_operation_id]


_TITLE_RE = re.compile(r"^\s*title\s+(.+?)\s*$", re.IGNORECASE)
_OPERATION_MARKER_RE = re.compile(r"^\s*'\s*operationId:\s*([A-Za-z0-9_.-]+)\s*$")
_PARTICIPANT_RE = re.compile(
    r"^\s*(actor|participant|database|collections|queue|entity|boundary|control)\s+(.+?)\s*$",
    re.IGNORECASE,
)
_MESSAGE_RE = re.compile(
    r"^\s*([A-Za-z0-9_.$]+)\s+[-.=ox]+[>x]?\s+([A-Za-z0-9_.$]+)\s*:?\s*(.*?)\s*$"
)


def parse_plantuml_sequence(source: str) -> ParsedPlantUMLDiagram:
    if "@startuml" not in source or "@enduml" not in source:
        raise PlantUMLParseError("PlantUML source must contain @startuml and @enduml")

    title = ""
    participants: list[PlantUMLParticipant] = []
    steps: list[DiagramStep] = []
    pending_operation_id: str | None = None

    for line_number, line in enumerate(source.splitlines(), start=1):
        title_match = _TITLE_RE.match(line)
        if title_match:
            title = title_match.group(1).strip()
            continue

        participant = _parse_participant(line, line_number)
        if participant:
            participants.append(participant)
            continue

        marker_match = _OPERATION_MARKER_RE.match(line)
        if marker_match:
            pending_operation_id = marker_match.group(1).strip()
            continue

        message_match = _MESSAGE_RE.match(line)
        if not message_match:
            continue

        sender, receiver, label = message_match.groups()
        steps.append(
            DiagramStep(
                step_id=f"step_{len(steps) + 1}",
                label=_message_label(sender, receiver, label),
                source_line=line_number,
                related_operation_id=pending_operation_id,
            )
        )
        pending_operation_id = None

    if not title:
        raise PlantUMLParseError("PlantUML sequence diagram is missing a title")

    return ParsedPlantUMLDiagram(
        title=title,
        diagram_type="sequence",
        participants=participants,
        steps=steps,
    )


def _parse_participant(line: str, line_number: int) -> PlantUMLParticipant | None:
    match = _PARTICIPANT_RE.match(line)
    if not match:
        return None

    kind, rest = match.groups()
    label, alias = _split_participant_alias(rest)
    return PlantUMLParticipant(
        alias=alias,
        label=label,
        kind=kind.lower(),
        source_line=line_number,
    )


def _split_participant_alias(rest: str) -> tuple[str, str]:
    if " as " in rest:
        raw_label, alias = re.split(r"\s+as\s+", rest, maxsplit=1, flags=re.IGNORECASE)
        label = raw_label.strip().strip('"')
        return label, alias.strip()

    value = rest.strip().strip('"')
    return value, value


def _message_label(sender: str, receiver: str, label: str) -> str:
    clean_label = label.strip()
    if clean_label:
        return clean_label
    return f"{sender} -> {receiver}"
