import assert from "node:assert/strict";
import test from "node:test";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { createReviewToolHandlers } from "../src/tools/review_tool_handlers.js";
import { FakeReviewServiceClient } from "./fixtures.js";

type SearchPayload = {
  results: Array<{ id: string; title: string; url: string }>;
};

type FetchPayload = {
  id: string;
  title: string;
  text: string;
  url: string;
  metadata: { related_openapi_operations?: string[] };
};

test("search returns the standard company-knowledge JSON text content shape", async () => {
  const handlers = createReviewToolHandlers(new FakeReviewServiceClient(), {
    publicBaseUrl: "https://review.example.test",
  });

  const result = await handlers.search({ query: "payment" });
  const content = textContent(result);
  const parsed = JSON.parse(content.text) as SearchPayload;

  assert.equal(result.content.length, 1);
  assert.deepEqual(parsed, result.structuredContent);
  assert.ok(parsed.results.length >= 1);
  assert.deepEqual(Object.keys(parsed.results[0]).sort(), ["id", "title", "url"]);
  assert.equal(parsed.results[0].id, "feature:checkout-payment");
  assert.equal(parsed.results[0].url, "https://review.example.test/features/checkout-payment");
});

test("fetch returns full text and metadata as one JSON text content item", async () => {
  const handlers = createReviewToolHandlers(new FakeReviewServiceClient(), {
    publicBaseUrl: "https://review.example.test",
  });

  const result = await handlers.fetch({ id: "doc:US-PAY-001" });
  const parsed = JSON.parse(textContent(result).text) as FetchPayload;

  assert.deepEqual(parsed, result.structuredContent);
  assert.equal(parsed.id, "doc:US-PAY-001");
  assert.equal(parsed.title, "Pay for an order");
  assert.match(parsed.text, /saved payment method/);
  assert.deepEqual(parsed.metadata.related_openapi_operations, ["createPayment"]);
});

test("fetch rejects unknown ids", async () => {
  const handlers = createReviewToolHandlers(new FakeReviewServiceClient(), {
    publicBaseUrl: "https://review.example.test",
  });

  await assert.rejects(() => handlers.fetch({ id: "doc:missing" }), /Unknown fetch id/);
});

function textContent(result: CallToolResult): { type: "text"; text: string } {
  const content = result.content[0];
  assert.equal(content.type, "text");
  return content as { type: "text"; text: string };
}
