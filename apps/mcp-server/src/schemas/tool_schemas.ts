import { z } from "zod";

export const featureIdInputSchema = {
  feature_id: z.string().min(1),
};

export const operationIdInputSchema = {
  operation_id: z.string().min(1),
};

export const diagramIdInputSchema = {
  diagram_id: z.string().min(1),
};

export const incidentIdInputSchema = {
  incident_id: z.string().min(1),
};

export const renderWorkspaceInputSchema = {
  feature_id: z.string().min(1).optional(),
  view: z
    .enum([
      "features",
      "overview",
      "docs",
      "diagram",
      "openapi",
      "incidents",
      "consistency",
      "test_gaps",
      "traceability",
      "source",
    ])
    .default("features"),
};

export const searchInputSchema = {
  query: z.string().min(1),
};

export const fetchInputSchema = {
  id: z.string().min(1),
};

export const featureListOutputSchema = {
  features: z.array(z.record(z.unknown())),
};

export const featureContextOutputSchema = {
  feature_id: z.string(),
  title: z.string(),
  domain: z.string(),
  user_story: z.record(z.unknown()),
  acceptance_criteria: z.record(z.unknown()).nullable(),
  incidents: z.array(z.record(z.unknown())),
  openapi_operations: z.array(z.record(z.unknown())),
  related_schemas: z.array(z.record(z.unknown())),
  diagrams: z.array(z.record(z.unknown())),
};

export const operationOutputSchema = {
  operation: z.record(z.unknown()),
};

export const diagramsOutputSchema = {
  feature_id: z.string(),
  diagrams: z.array(z.record(z.unknown())),
};

export const diagramOutputSchema = {
  diagram: z.record(z.unknown()),
};

export const auditOutputSchema = {
  audit: z.record(z.unknown()),
};

export const incidentImpactOutputSchema = {
  impact: z.record(z.unknown()),
};

export const testGapOutputSchema = {
  report: z.record(z.unknown()),
};

export const renderWorkspaceOutputSchema = {
  workspace: z.record(z.unknown()),
  features: z.array(z.record(z.unknown())).optional(),
};

export const searchOutputSchema = {
  results: z.array(
    z.object({
      id: z.string(),
      title: z.string(),
      url: z.string().url(),
    }),
  ),
};

export const fetchOutputSchema = {
  id: z.string(),
  title: z.string(),
  text: z.string(),
  url: z.string().url(),
  metadata: z.record(z.unknown()).optional(),
};
