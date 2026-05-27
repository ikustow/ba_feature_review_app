from __future__ import annotations

from functools import cached_property

from feature_review.api.config import ReviewServiceSettings, load_settings
from feature_review.api.models import IncidentImpactResponse, TestGapReportResponse
from feature_review.checks import audit_feature_consistency
from feature_review.data.diagram_loader import DiagramLoader
from feature_review.data.feature_catalog import FeatureCatalog, FeatureCatalogError
from feature_review.data.manifest_loader import load_manifest
from feature_review.models import FeatureAuditResult, FeatureContext, FeatureDiagram, FeatureSummary, ProductDoc
from feature_review.openapi.parser import load_openapi_spec
from feature_review.openapi.slicer import OpenAPISlicer


class ReviewServiceError(ValueError):
    """Raised when a review-service lookup cannot be fulfilled."""


class ReviewService:
    def __init__(self, settings: ReviewServiceSettings | None = None):
        self.settings = settings or load_settings()
        self._feature_context_cache: dict[str, FeatureContext] = {}
        self._diagram_cache: dict[str, FeatureDiagram] = {}

    @cached_property
    def manifest(self):
        return load_manifest(self.settings.manifest_path)

    @cached_property
    def openapi_spec(self):
        return load_openapi_spec(self.settings.openapi_path)

    @cached_property
    def openapi_slicer(self) -> OpenAPISlicer:
        return OpenAPISlicer(self.openapi_spec)

    @cached_property
    def catalog(self) -> FeatureCatalog:
        self.settings.diagram_svg_cache_dir.mkdir(parents=True, exist_ok=True)
        product_docs_root = self.settings.manifest_path.parent
        diagram_loader = DiagramLoader(
            product_docs_root,
            operation_index=self.openapi_slicer.index,
            svg_cache_dir=self.settings.diagram_svg_cache_dir,
        )
        return FeatureCatalog(
            manifest=self.manifest,
            product_docs_root=product_docs_root,
            openapi_slicer=self.openapi_slicer,
            diagram_loader=diagram_loader,
        )

    def health(self) -> str:
        return self.manifest.dataset_id

    def list_features(self) -> list[FeatureSummary]:
        return self.catalog.list_features()

    def get_feature_context(self, feature_id: str) -> FeatureContext:
        if feature_id not in self._feature_context_cache:
            try:
                self._feature_context_cache[feature_id] = self.catalog.get_feature_context(feature_id)
            except FeatureCatalogError as exc:
                raise ReviewServiceError(str(exc)) from exc
        return self._feature_context_cache[feature_id]

    def get_feature_diagrams(self, feature_id: str) -> list[FeatureDiagram]:
        return self.get_feature_context(feature_id).diagrams

    def get_diagram(self, diagram_id: str) -> FeatureDiagram:
        if diagram_id not in self._diagram_cache:
            for feature in self.list_features():
                for diagram in self.get_feature_diagrams(feature.feature_id):
                    self._diagram_cache[diagram.diagram_id] = diagram
        try:
            return self._diagram_cache[diagram_id]
        except KeyError as exc:
            raise ReviewServiceError(f"Unknown diagram id: {diagram_id}") from exc

    def get_openapi_operation(self, operation_id: str):
        try:
            return self.openapi_slicer.slice_operations([operation_id])[0]
        except ValueError as exc:
            raise ReviewServiceError(str(exc)) from exc

    def audit_feature(self, feature_id: str) -> FeatureAuditResult:
        return audit_feature_consistency(self.get_feature_context(feature_id))

    def audit_feature_diagram(self, feature_id: str) -> FeatureAuditResult:
        audit = self.audit_feature(feature_id)
        diagram_categories = {"diagram_operation_coverage", "diagram_branch_coverage"}
        findings = [finding for finding in audit.findings if finding.category in diagram_categories]
        return audit.model_copy(
            update={
                "review_id": f"{feature_id}:diagram_audit_v1",
                "overall_status": _overall_status(findings),
                "findings": findings,
                "generated_test_ideas": [],
                "recommended_next_actions": list(
                    dict.fromkeys(finding.recommended_action for finding in findings)
                ),
                "model_context_hint": (
                    "Diagram audit findings are deterministic checks over PlantUML operation markers, "
                    "feature manifest operations, and incident-affected operations."
                ),
            }
        )

    def analyze_incident_impact(self, incident_id: str) -> IncidentImpactResponse:
        related_contexts = [
            self.get_feature_context(feature.feature_id)
            for feature in self.list_features()
            if any(incident.document_id == incident_id for incident in self.get_feature_context(feature.feature_id).incidents)
        ]
        if not related_contexts:
            raise ReviewServiceError(f"Unknown or unlinked incident id: {incident_id}")

        incident = _incident_from_contexts(incident_id, related_contexts)
        findings = []
        test_ideas = []
        for context in related_contexts:
            audit = audit_feature_consistency(context)
            findings.extend(
                finding
                for finding in audit.findings
                if f"doc:{incident_id}" in finding.evidence_refs
            )
            test_ideas.extend(
                test_idea
                for test_idea in audit.generated_test_ideas
                if set(test_idea.related_operation_ids) & set(incident.related_openapi_operations)
            )

        return IncidentImpactResponse(
            incident_id=incident_id,
            incident=incident,
            related_feature_ids=[context.feature_id for context in related_contexts],
            findings=findings,
            generated_test_ideas=test_ideas,
            model_context_hint=(
                "Incident impact is derived from manifest traceability, related feature contexts, "
                "and deterministic audit findings citing the incident document."
            ),
        )

    def generate_test_gap_report(self, feature_id: str) -> TestGapReportResponse:
        audit = self.audit_feature(feature_id)
        test_gap_categories = {"response_coverage", "security_coverage", "incident_regression_coverage"}
        findings = [finding for finding in audit.findings if finding.category in test_gap_categories]
        return TestGapReportResponse(
            feature_id=feature_id,
            findings=findings,
            generated_test_ideas=audit.generated_test_ideas,
            model_context_hint=(
                "Test gaps are deterministic findings that imply missing negative, security, "
                "contract, boundary, or regression tests."
            ),
        )


def get_review_service() -> ReviewService:
    global _SERVICE
    try:
        return _SERVICE
    except NameError:
        _SERVICE = ReviewService()
        return _SERVICE


def _overall_status(findings) -> str:
    severities = {finding.severity for finding in findings}
    if "high" in severities:
        return "failed"
    if findings:
        return "warnings"
    return "passed"


def _incident_from_contexts(incident_id: str, contexts: list[FeatureContext]) -> ProductDoc:
    for context in contexts:
        for incident in context.incidents:
            if incident.document_id == incident_id:
                return incident
    raise ReviewServiceError(f"Unknown incident id: {incident_id}")
