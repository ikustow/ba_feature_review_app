from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from feature_review.models import (
    FeatureAuditResult,
    FeatureContext,
    FeatureDiagram,
    FeatureSummary,
    ProductDoc,
    RuleFinding,
    TestIdea,
)


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str = "feature-review-service"
    dataset_id: str


class FeatureListResponse(BaseModel):
    features: list[FeatureSummary]


class FeatureDiagramsResponse(BaseModel):
    feature_id: str
    diagrams: list[FeatureDiagram]


class IncidentImpactResponse(BaseModel):
    incident_id: str
    incident: ProductDoc
    related_feature_ids: list[str]
    findings: list[RuleFinding] = Field(default_factory=list)
    generated_test_ideas: list[TestIdea] = Field(default_factory=list)
    model_context_hint: str


class TestGapReportResponse(BaseModel):
    feature_id: str
    findings: list[RuleFinding] = Field(default_factory=list)
    generated_test_ideas: list[TestIdea] = Field(default_factory=list)
    model_context_hint: str


class DiagramAuditResponse(FeatureAuditResult):
    pass


class FeatureContextResponse(FeatureContext):
    pass
