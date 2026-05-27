import { useCallback, useState } from "react";
import type { ToolResult } from "../types.js";
import { callMcpTool } from "../lib/openai_bridge.js";

export function useCallTool() {
  const [loadingTool, setLoadingTool] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const callTool = useCallback(async (name: string, args: Record<string, unknown>): Promise<ToolResult> => {
    setLoadingTool(name);
    setError(null);
    try {
      return await callMcpTool(name, args);
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : "Tool call failed.";
      setError(message);
      throw cause;
    } finally {
      setLoadingTool(null);
    }
  }, []);

  return { callTool, loadingTool, error, clearError: () => setError(null) };
}
