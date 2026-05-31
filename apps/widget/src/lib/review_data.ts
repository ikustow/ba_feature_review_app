import type {
  FeatureAuditResult,
  FeatureContext,
  FeatureSummary,
  ProductDoc,
  ReviewWorkspaceData,
  RuleFinding,
  TestIdea,
  ToolResult,
  ViewKey,
  WorkspaceSummary,
} from "../types.js";

export const VIEW_KEYS: ViewKey[] = [
  "features",
  "overview",
  "docs",
  "openapi",
  "diagram",
  "incidents",
  "consistency",
  "test_gaps",
  "traceability",
  "source",
];

export function workspaceFromToolResult(result?: ToolResult): ReviewWorkspaceData {
  const structured = asRecord(result?.structuredContent);
  const meta = normalizeToolMeta(result?._meta);
  const metaFeatures = asArray<FeatureSummary>(meta.features);
  return {
    workspace: asWorkspaceSummary(structured.workspace),
    features: metaFeatures.length > 0 ? metaFeatures : asArray<FeatureSummary>(structured.features),
    context: asFeatureContext(meta.context ?? meta.full_context ?? structured.context ?? structured.full_context ?? structured),
    audit: asFeatureAudit(meta.audit ?? structured.audit),
    template_uri: asString(meta.template_uri ?? structured.template_uri),
  };
}

export function workspaceFromOpenAiGlobals(): ToolResult | undefined {
  const bridge = window.openai;
  if (!bridge?.toolOutput && !bridge?.toolResponseMetadata) return undefined;
  return {
    structuredContent: bridge.toolOutput ?? undefined,
    _meta: normalizeToolMeta(bridge.toolResponseMetadata ?? undefined),
  };
}

export function mergeWorkspaceData(
  current: ReviewWorkspaceData,
  patch: Partial<ReviewWorkspaceData>,
): ReviewWorkspaceData {
  return {
    workspace: patch.workspace ?? current.workspace,
    features: patch.features && patch.features.length > 0 ? patch.features : current.features,
    context: patch.context ?? current.context,
    audit: patch.audit ?? current.audit,
    template_uri: patch.template_uri ?? current.template_uri,
  };
}

export function contextFromResult(result: ToolResult): FeatureContext | undefined {
  const structured = asRecord(result.structuredContent);
  const meta = normalizeToolMeta(result._meta);
  return asFeatureContext(meta.full_context ?? meta.context ?? structured.full_context ?? structured.context ?? structured);
}

export function auditFromResult(result: ToolResult): FeatureAuditResult | undefined {
  const structured = asRecord(result.structuredContent);
  const audit = structured.audit ?? normalizeToolMeta(result._meta).audit;
  return asFeatureAudit(audit);
}

export function isViewKey(value: string | undefined): value is ViewKey {
  return Boolean(value && VIEW_KEYS.includes(value as ViewKey));
}

export function statusLabel(status?: string): string {
  switch (status) {
    case "passed":
      return "Passed";
    case "warnings":
      return "Warnings";
    case "failed":
      return "Failed";
    default:
      return "Not reviewed";
  }
}

export function methodTone(method: string): string {
  switch (method.toUpperCase()) {
    case "GET":
      return "tone-get";
    case "POST":
      return "tone-post";
    case "PUT":
    case "PATCH":
      return "tone-change";
    case "DELETE":
      return "tone-delete";
    default:
      return "tone-default";
  }
}

export function metadataText(doc: ProductDoc, key: string, fallback = "Not specified"): string {
  const value = doc.frontmatter[key];
  if (typeof value === "string" && value.trim()) return value;
  if (Array.isArray(value) && value.length > 0) return value.join(", ");
  return fallback;
}

export function formatJson(value: unknown): string {
  return JSON.stringify(value ?? null, null, 2);
}

export function sanitizeSvg(svg: string): string {
  return svg
    .replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, "")
    .replace(/\son[a-z]+\s*=\s*(['"]).*?\1/gi, "")
    .replace(/\s(href|xlink:href)\s*=\s*(['"])\s*javascript:.*?\2/gi, "");
}

export function buildFindingPrompt(finding: RuleFinding, context?: FeatureContext): string {
  const feature = context ? `${context.title} (${context.feature_id})` : "the selected feature";
  const evidence = finding.evidence_refs.length ? finding.evidence_refs.join(", ") : "no evidence refs";
  const operations = finding.affected_operation_ids.length
    ? finding.affected_operation_ids.join(", ")
    : "no affected operations";
  return [
    `Analyze this deterministic feature-review finding for ${feature}.`,
    `Finding: ${finding.title}`,
    `Severity: ${finding.severity}`,
    `Category: ${finding.category}`,
    `Description: ${finding.description}`,
    `Evidence: ${evidence}`,
    `Affected operations: ${operations}`,
    `Recommended action: ${finding.recommended_action}`,
    "Suggest the smallest documentation or test update that would resolve it.",
  ].join("\n");
}

export type TraceabilityRow = {
  userStory: string;
  acceptanceCriteria: string;
  diagramStep: string;
  operationId: string;
  incident: string;
  testIdea: string;
};

export function traceabilityRows(
  context?: FeatureContext,
  audit?: FeatureAuditResult,
): TraceabilityRow[] {
  if (!context) return [];
  const incidentsByOperation = new Map<string, ProductDoc[]>();
  for (const incident of context.incidents) {
    for (const operationId of incident.related_openapi_operations) {
      const bucket = incidentsByOperation.get(operationId) ?? [];
      bucket.push(incident);
      incidentsByOperation.set(operationId, bucket);
    }
  }

  const testsByOperation = new Map<string, TestIdea[]>();
  for (const testIdea of audit?.generated_test_ideas ?? []) {
    for (const operationId of testIdea.related_operation_ids) {
      const bucket = testsByOperation.get(operationId) ?? [];
      bucket.push(testIdea);
      testsByOperation.set(operationId, bucket);
    }
  }

  return context.openapi_operations.map((operation) => {
    const diagramStep = context.diagrams
      .flatMap((diagram) => diagram.steps)
      .find((step) => step.related_operation_id === operation.operation_id);
    return {
      userStory: context.user_story.document_id,
      acceptanceCriteria: context.acceptance_criteria?.document_id ?? "None",
      diagramStep: diagramStep ? `${diagramStep.step_id}: ${diagramStep.label}` : "Missing",
      operationId: operation.operation_id,
      incident: (incidentsByOperation.get(operation.operation_id) ?? [])
        .map((incident) => incident.document_id)
        .join(", ") || "None",
      testIdea: (testsByOperation.get(operation.operation_id) ?? [])
        .map((testIdea) => testIdea.test_id)
        .join(", ") || "None",
    };
  });
}

export function findingCountBySeverity(findings: RuleFinding[]): Record<RuleFinding["severity"], number> {
  return findings.reduce(
    (counts, finding) => {
      counts[finding.severity] += 1;
      return counts;
    },
    { low: 0, medium: 0, high: 0 },
  );
}

function normalizeToolMeta(value: unknown): Record<string, unknown> {
  if (!isRecord(value)) return {};
  const directMeta = value._meta;
  if (isRecord(directMeta)) return directMeta;
  const mcpToolResult = value.mcp_tool_result;
  if (isRecord(mcpToolResult) && isRecord(mcpToolResult._meta)) return mcpToolResult._meta;
  const callToolResult = value.call_tool_result;
  if (isRecord(callToolResult) && isRecord(callToolResult._meta)) return callToolResult._meta;
  return value;
}

function asWorkspaceSummary(value: unknown): WorkspaceSummary | undefined {
  return isRecord(value) ? (value as WorkspaceSummary) : undefined;
}

function asFeatureContext(value: unknown): FeatureContext | undefined {
  return isRecord(value) && typeof value.feature_id === "string" ? (value as FeatureContext) : undefined;
}

function asFeatureAudit(value: unknown): FeatureAuditResult | undefined {
  return isRecord(value) && typeof value.feature_id === "string" ? (value as FeatureAuditResult) : undefined;
}

function asString(value: unknown): string | undefined {
  return typeof value === "string" ? value : undefined;
}

function asArray<T>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : [];
}

function asRecord(value: unknown): Record<string, unknown> {
  return isRecord(value) ? value : {};
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
