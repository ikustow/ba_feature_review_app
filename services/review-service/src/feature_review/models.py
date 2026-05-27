from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field


class ProductArtifactType(StrEnum):
    USER_STORY = "user_story"
    ACCEPTANCE_CRITERIA = "acceptance_criteria"
    INCIDENT_NOTE = "incident_note"


class ManifestArtifactType(StrEnum):
    USER_STORY = "user_story"
    ACCEPTANCE_CRITERIA = "acceptance_criteria"
    INCIDENT_NOTE = "incident_note"
    UML_DIAGRAM = "uml_diagram"


class ProductDoc(BaseModel):
    document_id: str
    artifact_type: Literal["user_story", "acceptance_criteria", "incident_note"]
    title: str
    domain: str
    status: str
    version: str
    text: str
    frontmatter: dict[str, Any]
    related_openapi_operations: list[str] = Field(default_factory=list)
    path: str | None = None
    related_user_story: str | None = None
    related_diagrams: list[str] = Field(default_factory=list)


class FeatureSummary(BaseModel):
    feature_id: str
    title: str
    domain: str
    user_story_id: str
    acceptance_criteria_id: str | None = None
    related_operations_count: int
    diagram_count: int
    incident_count: int
    review_status: Literal["not_reviewed", "passed", "warnings", "failed"] = "not_reviewed"


class OpenAPIOperationSlice(BaseModel):
    operation_id: str
    method: str
    path: str
    summary: str | None = None
    description: str | None = None
    parameters: list[dict[str, Any]] = Field(default_factory=list)
    request_body: dict[str, Any] | None = None
    responses: dict[str, Any] = Field(default_factory=dict)
    security: list[dict[str, Any]] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    related_schema_names: list[str] = Field(default_factory=list)


class DiagramStep(BaseModel):
    step_id: str
    label: str
    source_line: int | None = None
    related_operation_id: str | None = None
    related_path: str | None = None


class FeatureDiagram(BaseModel):
    diagram_id: str
    feature_id: str
    title: str
    diagram_type: Literal["sequence", "activity", "component"]
    source: str = ""
    rendered_svg: str | None = None
    related_operation_ids: list[str] = Field(default_factory=list)
    steps: list[DiagramStep] = Field(default_factory=list)
    path: str | None = None


class FeatureContext(BaseModel):
    feature_id: str
    title: str
    domain: str
    user_story: ProductDoc
    acceptance_criteria: ProductDoc | None = None
    incidents: list[ProductDoc] = Field(default_factory=list)
    openapi_operations: list[OpenAPIOperationSlice] = Field(default_factory=list)
    related_schemas: list[dict[str, Any]] = Field(default_factory=list)
    diagrams: list[FeatureDiagram] = Field(default_factory=list)


class RuleFinding(BaseModel):
    finding_id: str
    severity: Literal["low", "medium", "high"]
    category: Literal[
        "operation_coverage",
        "response_coverage",
        "schema_required_fields",
        "enum_rules",
        "security_coverage",
        "diagram_operation_coverage",
        "diagram_branch_coverage",
        "incident_regression_coverage",
        "traceability",
        "open_question",
    ]
    title: str
    description: str
    evidence_refs: list[str] = Field(default_factory=list)
    affected_operation_ids: list[str] = Field(default_factory=list)
    recommended_action: str


class TestIdea(BaseModel):
    test_id: str
    title: str
    type: Literal["happy_path", "negative", "boundary", "security", "regression", "contract"]
    related_operation_ids: list[str] = Field(default_factory=list)
    given_when_then: str
    rationale: str


class FeatureAuditResult(BaseModel):
    review_id: str
    feature_id: str
    overall_status: Literal["passed", "warnings", "failed"]
    findings: list[RuleFinding] = Field(default_factory=list)
    generated_test_ideas: list[TestIdea] = Field(default_factory=list)
    recommended_next_actions: list[str] = Field(default_factory=list)
    model_context_hint: str


class ManifestEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    artifact_type: Literal["user_story", "acceptance_criteria", "incident_note", "uml_diagram"]
    path: str
    domain: str
    document_id: str | None = None
    diagram_id: str | None = None
    diagram_type: Literal["sequence", "activity", "component"] | None = None
    title: str | None = None
    related_user_story: str | None = None
    related_openapi_operations: list[str] = Field(default_factory=list)
    related_diagrams: list[str] = Field(default_factory=list)

    @computed_field
    @property
    def artifact_id(self) -> str:
        artifact_id = self.diagram_id if self.artifact_type == "uml_diagram" else self.document_id
        if not artifact_id:
            raise ValueError(f"Manifest {self.artifact_type!r} entry is missing an id")
        return artifact_id

    @property
    def is_product_doc(self) -> bool:
        return self.artifact_type in {
            ProductArtifactType.USER_STORY,
            ProductArtifactType.ACCEPTANCE_CRITERIA,
            ProductArtifactType.INCIDENT_NOTE,
        }


class DatasetManifest(BaseModel):
    dataset_id: str
    language: str
    source_type: str
    base_api_spec: str
    description: str
    counts: dict[str, int] = Field(default_factory=dict)
    documents: list[ManifestEntry]
    path: Path | None = None

    def entry_by_id(self, artifact_id: str) -> ManifestEntry:
        for entry in self.documents:
            if entry.artifact_id == artifact_id:
                return entry
        raise KeyError(f"Unknown manifest artifact id: {artifact_id}")

    @property
    def product_doc_entries(self) -> list[ManifestEntry]:
        return [entry for entry in self.documents if entry.is_product_doc]

    @property
    def diagram_entries(self) -> list[ManifestEntry]:
        return [entry for entry in self.documents if entry.artifact_type == "uml_diagram"]
