import type { FeatureAuditResult, FeatureContext, FeatureSummary, ToolResult, ViewKey } from "../types.js";

let fixturePromise: Promise<ToolResult> | undefined;

export function isLocalWidgetDev(): boolean {
  if (typeof window === "undefined") return false;
  const localHosts = new Set(["127.0.0.1", "localhost", "::1"]);
  return window.parent === window && localHosts.has(window.location.hostname);
}

export async function loadLocalDevToolResult(): Promise<ToolResult | undefined> {
  if (!isLocalWidgetDev()) return undefined;
  fixturePromise ??= fetch("/src/dev/mock_tool_result.json", { cache: "no-store" }).then(async (response) => {
    if (!response.ok) {
      throw new Error(`Local widget fixture failed to load (${response.status}).`);
    }
    return (await response.json()) as ToolResult;
  });
  return fixturePromise;
}

export async function callLocalDevTool(name: string, args: Record<string, unknown>): Promise<ToolResult> {
  const fixture = await loadLocalDevToolResult();
  if (!fixture) throw new Error("Local widget fixture is not available.");
  const meta = fixture?._meta ?? {};
  const features = asArray<FeatureSummary>(meta.features);
  const context = asFeatureContext(meta.context);
  const audit = asFeatureAudit(meta.audit);
  const featureId = typeof args.feature_id === "string" ? args.feature_id : context?.feature_id;
  const view = typeof args.view === "string" ? (args.view as ViewKey) : "overview";

  switch (name) {
    case "list_features":
      return {
        structuredContent: { features },
        content: [{ type: "text", text: `Found ${features.length} local fixture feature(s).` }],
      };
    case "get_feature_context":
      if (!context || (featureId && featureId !== context.feature_id)) {
        throw new Error(`Local fixture has no context for ${featureId ?? "unknown feature"}.`);
      }
      return {
        structuredContent: context,
        content: [{ type: "text", text: `Loaded local fixture context for ${context.title}.` }],
        _meta: { full_context: context },
      };
    case "audit_feature_consistency":
      if (!audit || (featureId && featureId !== audit.feature_id)) {
        throw new Error(`Local fixture has no audit for ${featureId ?? "unknown feature"}.`);
      }
      return {
        structuredContent: { audit },
        content: [{ type: "text", text: `Local fixture audit for ${audit.feature_id}: ${audit.overall_status}.` }],
      };
    case "render_feature_review_workspace":
      return {
        ...fixture,
        structuredContent: {
          workspace: {
            ...((fixture.structuredContent as { workspace?: Record<string, unknown> } | undefined)?.workspace ?? {}),
            view,
            feature_id: context?.feature_id ?? featureId ?? null,
            feature_title: context?.title ?? null,
          },
          features,
        },
      };
    default:
      throw new Error(`${name} is not available in the local widget fixture.`);
  }
}

function asArray<T>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : [];
}

function asFeatureContext(value: unknown): FeatureContext | undefined {
  return isRecord(value) && typeof value.feature_id === "string" ? (value as FeatureContext) : undefined;
}

function asFeatureAudit(value: unknown): FeatureAuditResult | undefined {
  return isRecord(value) && typeof value.feature_id === "string" ? (value as FeatureAuditResult) : undefined;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
