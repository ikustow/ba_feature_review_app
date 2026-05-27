import assert from "node:assert/strict";
import type { Server as HttpServer } from "node:http";
import test from "node:test";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { createHttpApp } from "../src/transport/http.js";
import { FEATURE_REVIEW_WORKSPACE_URI } from "../src/resources/feature_review_workspace_resource.js";
import { TOOL_DEFINITIONS } from "../src/tools/register_tools.js";
import { FakeReviewServiceClient } from "./fixtures.js";

test("HTTP app exposes health and MCP tool descriptors", async () => {
  const app = createHttpApp(new FakeReviewServiceClient(), {
    publicBaseUrl: "https://review.example.test",
  });
  const server = await listen(app);
  const port = (server.address() as { port: number }).port;
  const baseUrl = `http://127.0.0.1:${port}`;

  try {
    const healthResponse = await fetch(`${baseUrl}/health`);
    assert.equal(healthResponse.status, 200);
    assert.deepEqual(await healthResponse.json(), {
      status: "ok",
      service: "feature-review-mcp-server",
    });

    const client = new Client({
      name: "mcp-server-test-client",
      version: "0.1.0",
    });
    const transport = new StreamableHTTPClientTransport(new URL(`${baseUrl}/mcp`));

    await client.connect(transport);
    try {
      const tools = await client.listTools();
      assert.deepEqual(
        tools.tools.map((tool) => tool.name),
        [...TOOL_DEFINITIONS],
      );

      const renderTool = tools.tools.find((tool) => tool.name === "render_feature_review_workspace");
      assert.ok(renderTool);
      assert.equal(renderTool.annotations?.readOnlyHint, true);
      assert.equal(renderTool._meta?.["openai/outputTemplate"], FEATURE_REVIEW_WORKSPACE_URI);
      assert.equal((renderTool._meta?.ui as { resourceUri: string }).resourceUri, FEATURE_REVIEW_WORKSPACE_URI);
    } finally {
      await transport.close();
      await client.close();
    }
  } finally {
    await close(server);
  }
});

function listen(app: ReturnType<typeof createHttpApp>): Promise<HttpServer> {
  return new Promise((resolve) => {
    const server = app.listen(0, "127.0.0.1", () => resolve(server));
  });
}

function close(server: HttpServer): Promise<void> {
  return new Promise((resolve, reject) => {
    server.close((error) => {
      if (error) {
        reject(error);
      } else {
        resolve();
      }
    });
  });
}
