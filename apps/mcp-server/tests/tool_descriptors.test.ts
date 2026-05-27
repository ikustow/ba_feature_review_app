import assert from "node:assert/strict";
import test from "node:test";
import { RESOURCE_MIME_TYPE } from "@modelcontextprotocol/ext-apps/server";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { FEATURE_REVIEW_WORKSPACE_URI, registerFeatureReviewWorkspaceResource } from "../src/resources/feature_review_workspace_resource.js";
import { registerReviewTools, TOOL_DEFINITIONS } from "../src/tools/register_tools.js";
import { FakeReviewServiceClient } from "./fixtures.js";

test("registers read-only tool descriptors with app metadata only on render tool", () => {
  const registrations: Array<{ name: string; config: Record<string, unknown> }> = [];
  const server = {
    registerTool(name: string, config: Record<string, unknown>) {
      registrations.push({ name, config });
      return {};
    },
  } as unknown as McpServer;

  registerReviewTools(server, new FakeReviewServiceClient(), {
    publicBaseUrl: "https://review.example.test",
  });

  assert.deepEqual(
    registrations.map((registration) => registration.name),
    [...TOOL_DEFINITIONS],
  );

  for (const registration of registrations) {
    assert.deepEqual(registration.config.annotations, { readOnlyHint: true });
  }

  const renderTool = registrations.find((registration) => registration.name === "render_feature_review_workspace");
  assert.ok(renderTool);
  const renderMeta = renderTool.config._meta as Record<string, unknown>;
  assert.equal((renderMeta.ui as { resourceUri: string }).resourceUri, FEATURE_REVIEW_WORKSPACE_URI);
  assert.equal(renderMeta["openai/outputTemplate"], FEATURE_REVIEW_WORKSPACE_URI);
  assert.equal(renderMeta["ui/resourceUri"], FEATURE_REVIEW_WORKSPACE_URI);

  for (const registration of registrations.filter(
    (candidate) => candidate.name !== "render_feature_review_workspace",
  )) {
    const meta = registration.config._meta as Record<string, unknown> | undefined;
    assert.equal(meta?.["openai/outputTemplate"], undefined);
  }
});

test("registers the feature review workspace as an MCP app resource", async () => {
  const resources: Array<{
    name: string;
    uri: string;
    config: Record<string, unknown>;
    callback: (uri: URL, extra: unknown) => unknown;
  }> = [];
  const server = {
    registerResource(
      name: string,
      uri: string,
      config: Record<string, unknown>,
      callback: (uri: URL, extra: unknown) => unknown,
    ) {
      resources.push({ name, uri, config, callback });
      return {};
    },
  } as unknown as McpServer;

  registerFeatureReviewWorkspaceResource(server);

  assert.equal(resources.length, 1);
  assert.equal(resources[0].uri, FEATURE_REVIEW_WORKSPACE_URI);
  assert.equal(resources[0].config.mimeType, RESOURCE_MIME_TYPE);

  const resourceResult = (await resources[0].callback(
    new URL(FEATURE_REVIEW_WORKSPACE_URI),
    {},
  )) as {
    contents: Array<{
      uri: string;
      mimeType: string;
      text: string;
      _meta: {
        ui: {
          csp: { connectDomains: string[]; resourceDomains: string[] };
          prefersBorder: boolean;
        };
      };
    }>;
  };
  const content = resourceResult.contents[0];

  assert.equal(content.uri, FEATURE_REVIEW_WORKSPACE_URI);
  assert.equal(content.mimeType, RESOURCE_MIME_TYPE);
  assert.match(content.text, /Feature Review Workspace/);
  assert.deepEqual(content._meta.ui.csp.connectDomains, []);
  assert.deepEqual(content._meta.ui.csp.resourceDomains, []);
  assert.equal(content._meta.ui.prefersBorder, false);
});
