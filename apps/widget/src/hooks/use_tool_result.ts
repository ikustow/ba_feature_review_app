import { useEffect, useState } from "react";
import type { ToolResult } from "../types.js";
import { workspaceFromOpenAiGlobals } from "../lib/review_data.js";

export function useToolResult(): ToolResult | undefined {
  const [toolResult, setToolResult] = useState<ToolResult | undefined>(() => workspaceFromOpenAiGlobals());

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
