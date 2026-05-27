import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import type { ReviewServiceClient } from "../clients/review_service_client.js";
import type { McpServerConfig } from "../config.js";
import type { FeatureContext, FeatureDiagram } from "../types.js";
import { FEATURE_REVIEW_WORKSPACE_URI } from "../resources/feature_review_workspace_resource.js";
import { KnowledgeIndex } from "./knowledge_index.js";
import { compatibilityJsonResult, jsonToolResult } from "./tool_result.js";

export type ReviewToolHandlers = ReturnType<typeof createReviewToolHandlers>;

export function createReviewToolHandlers(
  client: ReviewServiceClient,
  config: Pick<McpServerConfig, "publicBaseUrl">,
) {
  const knowledgeIndex = new KnowledgeIndex(client, config.publicBaseUrl);

  return {
    async list_features(): Promise<CallToolResult> {
      const features = await client.listFeatures();
      return jsonToolResult(
        { features },
        `Found ${features.length} feature(s).`,
      );
    },

    async get_feature_context(args: { feature_id: string }): Promise<CallToolResult> {
      const context = await client.getFeatureContext(args.feature_id);
      return jsonToolResult(
        compactFeatureContext(context),
        `Loaded context for ${context.title}.`,
        { full_context: context },
      );
    },

    async get_openapi_operation(args: { operation_id: string }): Promise<CallToolResult> {
      const operation = await client.getOpenApiOperation(args.operation_id);
      return jsonToolResult(
        { operation },
        `Loaded OpenAPI operation ${operation.operation_id}.`,
      );
    },

    async get_feature_diagrams(args: { feature_id: string }): Promise<CallToolResult> {
      const diagrams = await client.getFeatureDiagrams(args.feature_id);
      return jsonToolResult(
        {
          feature_id: args.feature_id,
          diagrams: diagrams.map(compactDiagram),
        },
        `Loaded ${diagrams.length} diagram(s) for ${args.feature_id}.`,
        { diagrams },
      );
    },

    async get_diagram(args: { diagram_id: string }): Promise<CallToolResult> {
      const diagram = await client.getDiagram(args.diagram_id);
      return jsonToolResult(
        { diagram: compactDiagram(diagram) },
        `Loaded diagram ${diagram.diagram_id}.`,
        { diagram },
      );
    },

    async audit_feature_consistency(args: { feature_id: string }): Promise<CallToolResult> {
      const audit = await client.auditFeatureConsistency(args.feature_id);
      return jsonToolResult(
        { audit },
        `Feature audit for ${args.feature_id}: ${audit.overall_status}.`,
      );
    },

    async audit_diagram_consistency(args: { feature_id: string }): Promise<CallToolResult> {
      const audit = await client.auditDiagramConsistency(args.feature_id);
      return jsonToolResult(
        { audit },
        `Diagram audit for ${args.feature_id}: ${audit.overall_status}.`,
      );
    },

    async analyze_incident_impact(args: { incident_id: string }): Promise<CallToolResult> {
      const impact = await client.analyzeIncidentImpact(args.incident_id);
      return jsonToolResult(
        { impact },
        `Incident impact for ${args.incident_id}: ${impact.related_feature_ids.length} feature(s).`,
      );
    },

    async generate_test_gap_report(args: { feature_id: string }): Promise<CallToolResult> {
      const report = await client.generateTestGapReport(args.feature_id);
      return jsonToolResult(
        { report },
        `Generated test gap report for ${args.feature_id}.`,
      );
    },

    async render_feature_review_workspace(args: {
      feature_id?: string;
      view?: string;
    }): Promise<CallToolResult> {
      const features = await client.listFeatures();
      const selectedFeatureId = args.feature_id ?? features[0]?.feature_id;
      const context = selectedFeatureId ? await client.getFeatureContext(selectedFeatureId) : undefined;
      const audit = selectedFeatureId ? await client.auditFeatureConsistency(selectedFeatureId) : undefined;
      const workspace = {
        template_uri: FEATURE_REVIEW_WORKSPACE_URI,
        view: args.view ?? "features",
        feature_id: context?.feature_id ?? null,
        feature_title: context?.title ?? null,
        feature_count: features.length,
        finding_count: audit?.findings.length ?? 0,
        status: audit?.overall_status ?? "not_reviewed",
      };
      return jsonToolResult(
        { workspace },
        "Rendering Feature Review Workspace.",
        {
          features,
          context,
          audit,
          template_uri: FEATURE_REVIEW_WORKSPACE_URI,
        },
      );
    },

    async search(args: { query: string }): Promise<CallToolResult> {
      const output = await knowledgeIndex.search(args.query);
      return compatibilityJsonResult(output);
    },

    async fetch(args: { id: string }): Promise<CallToolResult> {
      const output = await knowledgeIndex.fetch(args.id);
      return compatibilityJsonResult(output);
    },
  };
}

function compactFeatureContext(context: FeatureContext) {
  return {
    feature_id: context.feature_id,
    title: context.title,
    domain: context.domain,
    user_story: context.user_story,
    acceptance_criteria: context.acceptance_criteria ?? null,
    incidents: context.incidents,
    openapi_operations: context.openapi_operations,
    related_schemas: context.related_schemas,
    diagrams: context.diagrams.map(compactDiagram),
  };
}

function compactDiagram(diagram: FeatureDiagram) {
  return {
    diagram_id: diagram.diagram_id,
    feature_id: diagram.feature_id,
    title: diagram.title,
    diagram_type: diagram.diagram_type,
    related_operation_ids: diagram.related_operation_ids,
    steps: diagram.steps,
    source: diagram.source,
    has_rendered_svg: Boolean(diagram.rendered_svg),
  };
}
