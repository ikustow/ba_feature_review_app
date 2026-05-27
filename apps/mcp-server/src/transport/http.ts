import express from "express";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import type { ReviewServiceClient } from "../clients/review_service_client.js";
import type { McpServerConfig } from "../config.js";
import { createMcpServer } from "../server.js";
import { registerHealthRoute } from "./health.js";

export function createHttpApp(
  client: ReviewServiceClient,
  config: Pick<McpServerConfig, "publicBaseUrl">,
) {
  const app = express();
  app.use(express.json({ limit: "8mb", type: "*/*" }));
  registerHealthRoute(app);

  app.all("/mcp", async (req, res) => {
    const server = createMcpServer(client, config);
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
    });
    res.on("close", () => {
      void transport.close();
      void server.close();
    });

    try {
      await server.connect(transport);
      await transport.handleRequest(req, res, req.body);
    } catch (error) {
      if (!res.headersSent) {
        res.status(500).json({
          jsonrpc: "2.0",
          error: {
            code: -32603,
            message: error instanceof Error ? error.message : "Internal MCP server error",
          },
          id: null,
        });
      }
    }
  });

  return app;
}
