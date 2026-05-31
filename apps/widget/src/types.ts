export type ViewKey =
  | "features"
  | "overview"
  | "docs"
  | "openapi"
  | "diagram"
  | "incidents"
  | "consistency"
  | "test_gaps"
  | "traceability"
  | "source";

export type FeatureSummary = {
  feature_id: string;
  title: string;
  domain: string;
  user_story_id: string;
  acceptance_criteria_id?: string | null;
  related_operations_count: number;
  diagram_count: number;
  incident_count: number;
  review_status?: "not_reviewed" | "passed" | "warnings" | "failed";
};

export type ProductDoc = {
  document_id: string;
  artifact_type: "user_story" | "acceptance_criteria" | "incident_note";
  title: string;
  domain: string;
  status: string;
  version: string;
  text: string;
  frontmatter: Record<string, unknown>;
  related_openapi_operations: string[];
  path?: string | null;
  related_user_story?: string | null;
  related_diagrams?: string[];
};

export type OpenApiOperationSlice = {
  operation_id: string;
  method: string;
  path: string;
  summary?: string | null;
  description?: string | null;
  parameters: Record<string, unknown>[];
  request_body?: Record<string, unknown> | null;
  responses: Record<string, unknown>;
  security: Record<string, unknown>[];
  tags: string[];
  related_schema_names: string[];
};

export type DiagramStep = {
  step_id: string;
  label: string;
  source_line?: number | null;
  related_operation_id?: string | null;
  related_path?: string | null;
};

export type FeatureDiagram = {
  diagram_id: string;
  feature_id: string;
  title: string;
  diagram_type: "sequence" | "activity" | "component";
  source: string;
  rendered_svg?: string | null;
  related_operation_ids: string[];
  steps: DiagramStep[];
  path?: string | null;
};

export type RuleFinding = {
  finding_id: string;
  severity: "low" | "medium" | "high";
  category: string;
  title: string;
  description: string;
  evidence_refs: string[];
  affected_operation_ids: string[];
  recommended_action: string;
};

export type TestIdea = {
  test_id: string;
  title: string;
  type: "happy_path" | "negative" | "boundary" | "security" | "regression" | "contract";
  related_operation_ids: string[];
  given_when_then: string;
  rationale: string;
};

export type FeatureContext = {
  feature_id: string;
  title: string;
  domain: string;
  user_story: ProductDoc;
  acceptance_criteria?: ProductDoc | null;
  incidents: ProductDoc[];
  openapi_operations: OpenApiOperationSlice[];
  related_schemas: Record<string, unknown>[];
  diagrams: FeatureDiagram[];
};

export type FeatureAuditResult = {
  review_id: string;
  feature_id: string;
  overall_status: "passed" | "warnings" | "failed";
  findings: RuleFinding[];
  generated_test_ideas: TestIdea[];
  recommended_next_actions: string[];
  model_context_hint: string;
};

export type WorkspaceSummary = {
  template_uri: string;
  view: ViewKey;
  feature_id: string | null;
  feature_title: string | null;
  feature_count: number;
  finding_count: number;
  status: "not_reviewed" | "passed" | "warnings" | "failed";
};

export type ReviewWorkspaceData = {
  workspace?: WorkspaceSummary;
  features: FeatureSummary[];
  context?: FeatureContext;
  audit?: FeatureAuditResult;
  template_uri?: string;
};

export type ToolContent = {
  type: string;
  text?: string;
};

export type ToolResult<TStructured = Record<string, unknown>> = {
  structuredContent?: TStructured;
  content?: ToolContent[];
  _meta?: Record<string, unknown>;
  isError?: boolean;
};

export type DisplayMode = "inline" | "fullscreen" | "pip" | string;

export type WidgetState = {
  selectedFeatureId?: string;
  activeView: ViewKey;
  selectedOperationId?: string;
  selectedStepId?: string;
  selectedFindingId?: string;
  showDiagramSource: boolean;
  diagramZoom: number;
  diagramPan: { x: number; y: number };
};

export type OpenAiBridge = {
  toolInput?: Record<string, unknown> | null;
  toolOutput?: Record<string, unknown> | null;
  toolResponseMetadata?: Record<string, unknown> | null;
  widgetState?: unknown;
  theme?: "light" | "dark";
  locale?: string;
  displayMode?: DisplayMode;
  callTool?: (name: string, args: Record<string, unknown>) => Promise<ToolResult>;
  sendFollowUpMessage?: (message: { prompt: string; scrollToBottom?: boolean }) => Promise<void> | void;
  setWidgetState?: (state: unknown) => void;
  notifyIntrinsicHeight?: (height: number) => void;
  requestDisplayMode?: (request: { mode: DisplayMode }) => Promise<void> | void;
  requestModal?: (request?: { params?: Record<string, unknown>; template?: string }) => Promise<void> | void;
  setOpenInAppUrl?: (request: { href: string }) => Promise<void> | void;
};

declare global {
  interface Window {
    openai?: OpenAiBridge;
  }
}
