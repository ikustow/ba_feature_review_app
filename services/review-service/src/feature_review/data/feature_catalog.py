from __future__ import annotations

import re
from pathlib import Path

from feature_review.data.diagram_loader import DiagramLoader
from feature_review.data.manifest_loader import load_manifest
from feature_review.data.markdown_loader import load_product_doc
from feature_review.data.paths import manifest_path, product_docs_dir
from feature_review.models import (
    DatasetManifest,
    FeatureContext,
    FeatureDiagram,
    FeatureSummary,
    OpenAPIOperationSlice,
    ProductDoc,
)
from feature_review.openapi.parser import default_openapi_path, load_openapi_spec
from feature_review.openapi.slicer import OpenAPISlicer


class FeatureCatalogError(ValueError):
    """Raised when feature catalog data cannot be assembled consistently."""


class FeatureCatalog:
    def __init__(
        self,
        manifest: DatasetManifest,
        product_docs_root: Path,
        openapi_slicer: OpenAPISlicer | None = None,
        diagram_loader: DiagramLoader | None = None,
    ):
        self.manifest = manifest
        self.product_docs_root = product_docs_root
        self.openapi_slicer = openapi_slicer
        self.diagram_loader = diagram_loader or DiagramLoader(
            product_docs_root,
            operation_index=openapi_slicer.index if openapi_slicer else None,
        )
        self._docs_by_id = self._load_product_docs()
        self._entries_by_id = {entry.artifact_id: entry for entry in manifest.documents}

    @classmethod
    def from_raw_data(cls, repo_root: Path | str | None = None) -> "FeatureCatalog":
        root = Path(repo_root) if repo_root is not None else None
        manifest = load_manifest(manifest_path(root))
        openapi_slicer = OpenAPISlicer(load_openapi_spec(default_openapi_path(root)))
        return cls(
            manifest=manifest,
            product_docs_root=product_docs_dir(root),
            openapi_slicer=openapi_slicer,
            diagram_loader=DiagramLoader(product_docs_dir(root), operation_index=openapi_slicer.index),
        )

    @classmethod
    def from_manifest_path(cls, path: Path | str) -> "FeatureCatalog":
        manifest = load_manifest(path)
        manifest_file = Path(path)
        spec_path = manifest_file.parent.parent / "openapi.yaml"
        openapi_slicer = OpenAPISlicer(load_openapi_spec(spec_path)) if spec_path.exists() else None
        return cls(
            manifest=manifest,
            product_docs_root=manifest_file.parent,
            openapi_slicer=openapi_slicer,
            diagram_loader=DiagramLoader(
                manifest_file.parent,
                operation_index=openapi_slicer.index if openapi_slicer else None,
            ),
        )

    def list_features(self) -> list[FeatureSummary]:
        return [self._summary_for_story(story) for story in self._user_stories()]

    def get_feature_context(self, feature_id: str) -> FeatureContext:
        try:
            user_story = self._docs_by_id[feature_id]
        except KeyError as exc:
            raise FeatureCatalogError(f"Unknown feature id: {feature_id}") from exc

        if user_story.artifact_type != "user_story":
            raise FeatureCatalogError(f"Feature id must reference a user story: {feature_id}")

        return FeatureContext(
            feature_id=user_story.document_id,
            title=feature_title(user_story.title),
            domain=user_story.domain,
            user_story=user_story,
            acceptance_criteria=self._acceptance_criteria_for(user_story.document_id),
            incidents=self._incidents_for(user_story),
            openapi_operations=self._openapi_operations_for(user_story),
            related_schemas=self._related_schemas_for(user_story),
            diagrams=self._diagrams_for(user_story),
        )

    def _load_product_docs(self) -> dict[str, ProductDoc]:
        docs: dict[str, ProductDoc] = {}
        for entry in self.manifest.product_doc_entries:
            doc_path = self.product_docs_root / entry.path
            doc = load_product_doc(doc_path, manifest_entry=entry)
            docs[doc.document_id] = doc
        return docs

    def _user_stories(self) -> list[ProductDoc]:
        return [
            self._docs_by_id[entry.artifact_id]
            for entry in self.manifest.product_doc_entries
            if entry.artifact_type == "user_story"
        ]

    def _summary_for_story(self, story: ProductDoc) -> FeatureSummary:
        acceptance_criteria = self._acceptance_criteria_for(story.document_id)
        incidents = self._incidents_for(story)
        story_entry = self._entries_by_id.get(story.document_id)
        diagram_ids = story.related_diagrams or (story_entry.related_diagrams if story_entry else [])
        return FeatureSummary(
            feature_id=story.document_id,
            title=feature_title(story.title),
            domain=story.domain,
            user_story_id=story.document_id,
            acceptance_criteria_id=acceptance_criteria.document_id if acceptance_criteria else None,
            related_operations_count=len(story.related_openapi_operations),
            diagram_count=len(diagram_ids),
            incident_count=len(incidents),
        )

    def _acceptance_criteria_for(self, user_story_id: str) -> ProductDoc | None:
        for doc in self._docs_by_id.values():
            if doc.artifact_type == "acceptance_criteria" and doc.related_user_story == user_story_id:
                return doc
        return None

    def _incidents_for(self, story: ProductDoc) -> list[ProductDoc]:
        story_operations = set(story.related_openapi_operations)
        incidents: list[ProductDoc] = []
        for doc in self._docs_by_id.values():
            if doc.artifact_type != "incident_note" or doc.domain != story.domain:
                continue
            incident_operations = set(doc.related_openapi_operations)
            if incident_operations and incident_operations.issubset(story_operations):
                incidents.append(doc)
        return incidents

    def _diagrams_for(self, story: ProductDoc) -> list[FeatureDiagram]:
        story_entry = self._entries_by_id.get(story.document_id)
        diagram_ids = story.related_diagrams or (story_entry.related_diagrams if story_entry else [])
        diagrams: list[FeatureDiagram] = []
        for diagram_id in diagram_ids:
            entry = self._entries_by_id.get(diagram_id)
            if entry is None or entry.artifact_type != "uml_diagram":
                raise FeatureCatalogError(f"Unknown related diagram id {diagram_id!r} for {story.document_id}")
            diagrams.append(self.diagram_loader.load_manifest_diagram(entry, story.document_id))
        return diagrams

    def _openapi_operations_for(self, story: ProductDoc) -> list[OpenAPIOperationSlice]:
        if self.openapi_slicer is None:
            return []
        return self.openapi_slicer.slice_operations(story.related_openapi_operations)

    def _related_schemas_for(self, story: ProductDoc) -> list[dict]:
        if self.openapi_slicer is None:
            return []
        return self.openapi_slicer.related_schemas_for_operations(story.related_openapi_operations)


def feature_title(document_title: str) -> str:
    return re.sub(r"^(User Story|Acceptance Criteria|Incident Note):\s*", "", document_title).strip()
