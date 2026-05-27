import type { Express } from "express";

export function registerHealthRoute(app: Express): void {
  app.get("/health", (_req, res) => {
    res.json({ status: "ok", service: "feature-review-mcp-server" });
  });
}
