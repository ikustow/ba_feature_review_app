from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from feature_review.api.models import (
    DiagramAuditResponse,
    FeatureContextResponse,
    FeatureDiagramsResponse,
    FeatureListResponse,
    HealthResponse,
    IncidentImpactResponse,
    TestGapReportResponse,
)
from feature_review.api.service import ReviewService, ReviewServiceError, get_review_service
from feature_review.models import FeatureAuditResult, FeatureDiagram, OpenAPIOperationSlice


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(service: ReviewService = Depends(get_review_service)) -> HealthResponse:
    return HealthResponse(status="ok", dataset_id=service.health())


@router.get("/features", response_model=FeatureListResponse)
def list_features(service: ReviewService = Depends(get_review_service)) -> FeatureListResponse:
    return FeatureListResponse(features=service.list_features())


@router.get("/features/{feature_id}", response_model=FeatureContextResponse)
def get_feature_context(
    feature_id: str,
    service: ReviewService = Depends(get_review_service),
):
    return _or_404(lambda: service.get_feature_context(feature_id))


@router.get("/features/{feature_id}/diagrams", response_model=FeatureDiagramsResponse)
def get_feature_diagrams(
    feature_id: str,
    service: ReviewService = Depends(get_review_service),
) -> FeatureDiagramsResponse:
    diagrams = _or_404(lambda: service.get_feature_diagrams(feature_id))
    return FeatureDiagramsResponse(feature_id=feature_id, diagrams=diagrams)


@router.get("/diagrams/{diagram_id}", response_model=FeatureDiagram)
def get_diagram(
    diagram_id: str,
    service: ReviewService = Depends(get_review_service),
):
    return _or_404(lambda: service.get_diagram(diagram_id))


@router.get("/openapi/operations/{operation_id}", response_model=OpenAPIOperationSlice)
def get_openapi_operation(
    operation_id: str,
    service: ReviewService = Depends(get_review_service),
):
    return _or_404(lambda: service.get_openapi_operation(operation_id))


@router.post("/features/{feature_id}/audit", response_model=FeatureAuditResult)
def audit_feature(
    feature_id: str,
    service: ReviewService = Depends(get_review_service),
):
    return _or_404(lambda: service.audit_feature(feature_id))


@router.post("/features/{feature_id}/diagram-audit", response_model=DiagramAuditResponse)
def audit_feature_diagram(
    feature_id: str,
    service: ReviewService = Depends(get_review_service),
):
    return _or_404(lambda: service.audit_feature_diagram(feature_id))


@router.post("/incidents/{incident_id}/impact", response_model=IncidentImpactResponse)
def analyze_incident_impact(
    incident_id: str,
    service: ReviewService = Depends(get_review_service),
):
    return _or_404(lambda: service.analyze_incident_impact(incident_id))


@router.post("/features/{feature_id}/test-gaps", response_model=TestGapReportResponse)
def generate_test_gap_report(
    feature_id: str,
    service: ReviewService = Depends(get_review_service),
):
    return _or_404(lambda: service.generate_test_gap_report(feature_id))


def _or_404(callback):
    try:
        return callback()
    except ReviewServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
