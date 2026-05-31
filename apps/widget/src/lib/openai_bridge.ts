import type { ToolResult } from "../types.js";
import { callLocalDevTool, isLocalWidgetDev } from "./local_dev_fixture.js";

let requestCounter = 0;

type JsonRpcResponse = {
  jsonrpc: "2.0";
  id: number;
  result?: unknown;
  error?: { message?: string };
};

export function postJsonRpcNotification(method: string, params: Record<string, unknown>): void {
  window.parent.postMessage(
    {
      jsonrpc: "2.0",
      method,
      params,
    },
    "*",
  );
}

export function postJsonRpcRequest<TResponse>(
  method: string,
  params: Record<string, unknown>,
  timeoutMs = 8000,
): Promise<TResponse> {
  const id = ++requestCounter;
  return new Promise((resolve, reject) => {
    const timer = window.setTimeout(() => {
      window.removeEventListener("message", onMessage);
      reject(new Error(`${method} timed out.`));
    }, timeoutMs);

    function onMessage(event: MessageEvent<JsonRpcResponse>) {
      if (event.source !== window.parent) return;
      const message = event.data;
      if (!message || message.jsonrpc !== "2.0" || message.id !== id) return;
      window.clearTimeout(timer);
      window.removeEventListener("message", onMessage);
      if (message.error) {
        reject(new Error(message.error.message ?? `${method} failed.`));
      } else {
        resolve(message.result as TResponse);
      }
    }

    window.addEventListener("message", onMessage);
    window.parent.postMessage(
      {
        jsonrpc: "2.0",
        id,
        method,
        params,
      },
      "*",
    );
  });
}

export async function callMcpTool(
  name: string,
  args: Record<string, unknown>,
): Promise<ToolResult> {
  if (window.openai?.callTool) {
    return window.openai.callTool(name, args);
  }
  if (isLocalWidgetDev()) {
    return callLocalDevTool(name, args);
  }
  return postJsonRpcRequest<ToolResult>("tools/call", {
    name,
    arguments: args,
  });
}

export async function sendFollowUpMessage(
  prompt: string,
  options: { scrollToBottom?: boolean } = {},
): Promise<void> {
  if (window.openai?.sendFollowUpMessage) {
    await window.openai.sendFollowUpMessage({
      prompt,
      scrollToBottom: options.scrollToBottom ?? true,
    });
    return;
  }
  postJsonRpcNotification("ui/message", {
    role: "user",
    content: [{ type: "text", text: prompt }],
  });
}

export async function updateModelContext(text: string, structuredContent?: Record<string, unknown>): Promise<void> {
  try {
    await postJsonRpcRequest("ui/update-model-context", {
      content: [{ type: "text", text }],
      structuredContent,
    });
  } catch {
    // Some hosts expose follow-up messages but not model-context updates to widgets.
  }
}

export function notifyIntrinsicHeight(): void {
  const height = Math.ceil(document.documentElement.getBoundingClientRect().height);
  window.openai?.notifyIntrinsicHeight?.(height);
}

export async function requestWorkspaceDisplayMode(mode: "fullscreen" | "pip"): Promise<boolean> {
  if (!window.openai?.requestDisplayMode) return false;
  await window.openai.requestDisplayMode({ mode });
  return true;
}
