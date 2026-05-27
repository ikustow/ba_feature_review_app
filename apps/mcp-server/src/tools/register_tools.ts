import { registerAppTool } from "@modelcontextprotocol/ext-apps/server";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { ToolAnnotations } from "@modelcontextprotocol/sdk/types.js";
import type { ReviewServiceClient } from "../clients/review_service_client.js";
import type { McpServerConfig } from "../config.js";
import { FEATURE_REVIEW_WORKSPACE_URI } from "../resources/feature_review_workspace_resource.js";
import {
  auditOutputSchema,
  diagramIdInputSchema,
  diagramOutputSchema,
  diagramsOutputSchema,
  fetchInputSchema,
  fetchOutputSchema,
  featureContextOutputSchema,
  featureIdInputSchema,
  featureListOutputSchema,
  incidentIdInputSchema,
  incidentImpactOutputSchema,
  operationIdInputSchema,
  operationOutputSchema,
  renderWorkspaceInputSchema,
  renderWorkspaceOutputSchema,
  searchInputSchema,
  searchOutputSchema,
  testGapOutputSchema,
} from "../schemas/tool_schemas.js";
import { createReviewToolHandlers } from "./review_tool_handlers.js";

const READ_ONLY: ToolAnnotations = { readOnlyHint: true };

export const TOOL_DEFINITIONS = [
  "list_features",
  "get_feature_context",
  "get_openapi_operation",
  "get_feature_diagrams",
  "get_diagram",
  "audit_feature_consistency",
  "audit_diagram_consistency",
  "analyze_incident_impact",
  "generate_test_gap_report",
  "render_feature_review_workspace",
  "search",
  "fetch",
] as const;

export function registerReviewTools(
  server: McpServer,
  client: ReviewServiceClient,
  config: Pick<McpServerConfig, "publicBaseUrl">,
): void {
  const handlers = createReviewToolHandlers(client, config);

  server.registerTool(
    "list_features",
    {
      title: "List Features",
      description: "List read-only feature summaries from the synthetic product documentation manifest.",
      outputSchema: featureListOutputSchema,
      annotations: READ_ONLY,
    },
    handlers.list_features,
  );

  server.registerTool(
    "get_feature_context",
    {
      title: "Get Feature Context",
      description: "Return docs, incidents, compact OpenAPI slices, related schemas, and diagram summaries for a feature.",
      inputSchema: featureIdInputSchema,
      outputSchema: featureContextOutputSchema,
      annotations: READ_ONLY,
    },
    handlers.get_feature_context,
  );

  server.registerTool(
    "get_openapi_operation",
    {
      title: "Get OpenAPI Operation",
      description: "Return one compact OpenAPI operation slice by operationId.",
      inputSchema: operationIdInputSchema,
      outputSchema: operationOutputSchema,
      annotations: READ_ONLY,
    },
    handlers.get_openapi_operation,
  );

  server.registerTool(
    "get_feature_diagrams",
    {
      title: "Get Feature Diagrams",
      description: "Return PlantUML source, rendered SVG metadata, steps, and operation markers for a feature.",
      inputSchema: featureIdInputSchema,
      outputSchema: diagramsOutputSchema,
      annotations: READ_ONLY,
    },
    handlers.get_feature_diagrams,
  );

  server.registerTool(
    "get_diagram",
    {
      title: "Get Diagram",
      description: "Return a single PlantUML diagram by diagram id.",
      inputSchema: diagramIdInputSchema,
      outputSchema: diagramOutputSchema,
      annotations: READ_ONLY,
    },
    handlers.get_diagram,
  );

  server.registerTool(
    "audit_feature_consistency",
    {
      title: "Audit Feature Consistency",
      description: "Run deterministic checks across product docs, incidents, diagrams, and OpenAPI slices.",
      inputSchema: featureIdInputSchema,
      outputSchema: auditOutputSchema,
      annotations: READ_ONLY,
    },
    handlers.audit_feature_consistency,
  );

  server.registerTool(
    "audit_diagram_consistency",
    {
      title: "Audit Diagram Consistency",
      description: "Run deterministic checks focused on feature diagram operation coverage and incident coverage.",
      inputSchema: featureIdInputSchema,
      outputSchema: auditOutputSchema,
      annotations: READ_ONLY,
    },
    handlers.audit_diagram_consistency,
  );

  server.registerTool(
    "analyze_incident_impact",
    {
      title: "Analyze Incident Impact",
      description: "Return features, findings, and test ideas related to one incident note.",
      inputSchema: incidentIdInputSchema,
      outputSchema: incidentImpactOutputSchema,
      annotations: READ_ONLY,
    },
    handlers.analyze_incident_impact,
  );

  server.registerTool(
    "generate_test_gap_report",
    {
      title: "Generate Test Gap Report",
      description: "Return deterministic missing-test findings and generated test ideas for a feature.",
      inputSchema: featureIdInputSchema,
      outputSchema: testGapOutputSchema,
      annotations: READ_ONLY,
    },
    handlers.generate_test_gap_report,
  );

  registerAppTool(
    server,
    "render_feature_review_workspace",
    {
      title: "Render Feature Review Workspace",
      description: "Render the widget after data tools have prepared feature review context.",
      inputSchema: renderWorkspaceInputSchema,
      outputSchema: renderWorkspaceOutputSchema,
      annotations: READ_ONLY,
      _meta: {
        ui: { resourceUri: FEATURE_REVIEW_WORKSPACE_URI },
        "openai/outputTemplate": FEATURE_REVIEW_WORKSPACE_URI,
        "openai/toolInvocation/invoking": "Opening feature review workspace...",
        "openai/toolInvocation/invoked": "Feature review workspace ready.",
      },
    },
    handlers.render_feature_review_workspace,
  );

  server.registerTool(
    "search",
    {
      title: "Search Feature Review Knowledge",
      description: "Search feature docs, incidents, diagrams, and operation slices by query.",
      inputSchema: searchInputSchema,
      outputSchema: searchOutputSchema,
      annotations: READ_ONLY,
    },
    handlers.search,
  );

  server.registerTool(
    "fetch",
    {
      title: "Fetch Feature Review Knowledge Item",
      description: "Fetch the full text and metadata for a search result id.",
      inputSchema: fetchInputSchema,
      outputSchema: fetchOutputSchema,
      annotations: READ_ONLY,
    },
    handlers.fetch,
  );
}
