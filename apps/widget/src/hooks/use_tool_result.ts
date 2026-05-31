import { useEffect, useState } from "react";
import type { ToolResult } from "../types.js";
import { loadLocalDevToolResult } from "../lib/local_dev_fixture.js";
import { workspaceFromOpenAiGlobals } from "../lib/review_data.js";

export function useToolResult(): ToolResult | undefined {
  const [toolResult, setToolResult] = useState<ToolResult | undefined>(() => workspaceFromOpenAiGlobals());

  useEffect(() => {
    if (toolResult) return;
    let cancelled = false;
    void loadLocalDevToolResult()
      .then((localResult) => {
        if (!cancelled && localResult) setToolResult(localResult);
      })
      .catch(() => {
        // Local fixtures are best-effort; ChatGPT-hosted widgets should stay quiet.
      });
    return () => {
      cancelled = true;
    };
  }, [toolResult]);

  useEffect(() => {
    function onMessage(event: MessageEvent) {
      if (event.source !== window.parent) return;
      const message = event.data;
      if (!message || message.jsonrpc !== "2.0") return;
      if (message.method === "ui/notifications/tool-result") {
        setToolResult(message.params as ToolResult);
      }
    }

    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, []);

  return toolResult;
}
