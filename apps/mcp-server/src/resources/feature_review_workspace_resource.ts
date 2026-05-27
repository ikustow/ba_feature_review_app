import { RESOURCE_MIME_TYPE, registerAppResource } from "@modelcontextprotocol/ext-apps/server";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

export const FEATURE_REVIEW_WORKSPACE_URI = "ui://widget/feature-review-workspace-v1.html";

export function registerFeatureReviewWorkspaceResource(server: McpServer): void {
  registerAppResource(
    server,
    "Feature Review Workspace",
    FEATURE_REVIEW_WORKSPACE_URI,
    {
      title: "Feature Review Workspace",
      description: "Read-only workspace for feature docs, OpenAPI slices, diagrams, and findings.",
      _meta: {
        ui: {
          csp: {
            connectDomains: [],
            resourceDomains: [],
          },
          prefersBorder: false,
        },
        "openai/widgetDescription":
          "Shows a read-only feature review workspace with docs, diagrams, OpenAPI operations, incidents, findings, and test gaps.",
      },
    },
    async () => ({
      contents: [
        {
          uri: FEATURE_REVIEW_WORKSPACE_URI,
          mimeType: RESOURCE_MIME_TYPE,
          text: workspaceHtml,
          _meta: {
            ui: {
              csp: {
                connectDomains: [],
                resourceDomains: [],
              },
              prefersBorder: false,
            },
            "openai/widgetDescription":
              "Shows a read-only feature review workspace with docs, diagrams, OpenAPI operations, incidents, findings, and test gaps.",
          },
        },
      ],
    }),
  );
}

const workspaceHtml = `
<main id="root" style="font-family: system-ui, sans-serif; padding: 16px; color: #111827;">
  <h1 style="font-size: 18px; margin: 0 0 8px;">Feature Review Workspace</h1>
  <p id="summary" style="margin: 0 0 12px; color: #4b5563;">Waiting for feature review data.</p>
  <pre id="payload" style="white-space: pre-wrap; font-size: 12px; border: 1px solid #d1d5db; padding: 12px; overflow: auto;"></pre>
</main>
<script>
  const root = document.getElementById("payload");
  const summary = document.getElementById("summary");
  function render(toolResult) {
    const data = toolResult && toolResult.structuredContent ? toolResult.structuredContent : {};
    const meta = toolResult && toolResult._meta ? toolResult._meta : {};
    const workspace = data.workspace || {};
    summary.textContent = workspace.feature_title
      ? workspace.feature_title + " · " + (workspace.view || "overview")
      : "Feature Review Workspace";
    root.textContent = JSON.stringify({ workspace, meta }, null, 2);
  }
  window.addEventListener("message", (event) => {
    if (event.source !== window.parent) return;
    const message = event.data;
    if (!message || message.jsonrpc !== "2.0") return;
    if (message.method === "ui/notifications/tool-result") render(message.params);
  }, { passive: true });
</script>
`.trim();
