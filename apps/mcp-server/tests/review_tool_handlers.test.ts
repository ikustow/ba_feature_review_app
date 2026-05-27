import assert from "node:assert/strict";
import test from "node:test";
import { FEATURE_REVIEW_WORKSPACE_URI } from "../src/resources/feature_review_workspace_resource.js";
import { createReviewToolHandlers } from "../src/tools/review_tool_handlers.js";
import { FakeReviewServiceClient } from "./fixtures.js";

test("feature context keeps structured content compact and full payload in _meta", async () => {
  const handlers = createReviewToolHandlers(new FakeReviewServiceClient(), {
    publicBaseUrl: "https://review.example.test",
  });

  const result = await handlers.get_feature_context({ feature_id: "checkout-payment" });
  const structured = result.structuredContent as Record<string, unknown>;
  const meta = result._meta as Record<string, unknown>;

  assert.equal(structured.feature_id, "checkout-payment");
  assert.ok(Array.isArray(structured.openapi_operations));
  assert.equal((meta.full_context as { title: string }).title, "Checkout Payment");
});

test("diagram tools keep rendered SVG in _meta and expose PlantUML source", async () => {
  const handlers = createReviewToolHandlers(new FakeReviewServiceClient(), {
    publicBaseUrl: "https://review.example.test",
  });

  const result = await handlers.get_diagram({ diagram_id: "D-PAY-001" });
  const structured = result.structuredContent as {
    diagram: { source: string; has_rendered_svg: boolean; rendered_svg?: string };
  };
  const meta = result._meta as { diagram: { rendered_svg: string } };

  assert.match(structured.diagram.source, /@startuml/);
  assert.equal(structured.diagram.has_rendered_svg, true);
  assert.equal(structured.diagram.rendered_svg, undefined);
  assert.match(meta.diagram.rendered_svg, /<svg/);
});

test("render tool returns widget summary in structuredContent and workspace data in _meta", async () => {
  const handlers = createReviewToolHandlers(new FakeReviewServiceClient(), {
    publicBaseUrl: "https://review.example.test",
  });

  const result = await handlers.render_feature_review_workspace({
    feature_id: "checkout-payment",
    view: "diagram",
  });
  const structured = result.structuredContent as { workspace: Record<string, unknown> };
  const meta = result._meta as Record<string, unknown>;

  assert.equal(structured.workspace.template_uri, FEATURE_REVIEW_WORKSPACE_URI);
  assert.equal(structured.workspace.view, "diagram");
  assert.equal(structured.workspace.feature_id, "checkout-payment");
  assert.equal(structured.workspace.finding_count, 1);
  assert.ok(Array.isArray(meta.features));
  assert.equal((meta.context as { feature_id: string }).feature_id, "checkout-payment");
  assert.equal((meta.audit as { overall_status: string }).overall_status, "warnings");
});
