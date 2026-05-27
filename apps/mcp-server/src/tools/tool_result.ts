import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

export function jsonToolResult<TStructured extends Record<string, unknown>>(
  structuredContent: TStructured,
  text: string,
  meta?: Record<string, unknown>,
): CallToolResult {
  return {
    structuredContent,
    content: [{ type: "text", text }],
    _meta: meta,
  };
}

export function compatibilityJsonResult<TStructured extends Record<string, unknown>>(
  structuredContent: TStructured,
): CallToolResult {
  return {
    structuredContent,
    content: [{ type: "text", text: JSON.stringify(structuredContent) }],
  };
}
