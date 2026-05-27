import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { ReviewServiceClient } from "./clients/review_service_client.js";
import type { McpServerConfig } from "./config.js";
import { registerFeatureReviewWorkspaceResource } from "./resources/feature_review_workspace_resource.js";
import { registerReviewTools } from "./tools/register_tools.js";

export function createMcpServer(
  client: ReviewServiceClient,
  config: Pick<McpServerConfig, "publicBaseUrl">,
): McpServer {
  const server = new McpServer(
    {
      name: "ai-feature-review",
      version: "0.1.0",
    },
    {
      capabilities: {
        tools: {},
        resources: {},
      },
      instructions:
        "Read-only AI Feature Review app. Use tools to inspect feature docs, OpenAPI slices, PlantUML diagrams, incidents, deterministic findings, and test gaps. Do not mutate source files.",
    },
  );

  registerFeatureReviewWorkspaceResource(server);
  registerReviewTools(server, client, config);
  return server;
}
