import assert from "node:assert/strict";
import test from "node:test";
import {
  buildFindingPrompt,
  contextFromResult,
  sanitizeSvg,
  traceabilityRows,
  workspaceFromToolResult,
} from "../src/lib/review_data.js";
import type { FeatureAuditResult, FeatureContext, RuleFinding, ToolResult } from "../src/types.js";

const finding: RuleFinding = {
  finding_id: "finding-1",
  severity: "medium",
  category: "diagram_operation_coverage",
  title: "Diagram omits createPayment",
  description: "The diagram does not reference the payment operation.",
  evidence_refs: ["D-PAY-001", "createPayment"],
  affected_operation_ids: ["createPayment"],
  recommended_action: "Add the operation marker to the diagram step.",
};

const context: FeatureContext = {
  feature_id: "checkout-payment",
  title: "Checkout Payment",
  domain: "payments",
  user_story: {
    document_id: "US-PAY-001",
    artifact_type: "user_story",
    title: "Pay for an order",
    domain: "payments",
    status: "approved",
    version: "1.0",
    text: "As a shopper, I can pay.",
    frontmatter: {},
    related_openapi_operations: ["createPayment"],
  },
  acceptance_criteria: {
    document_id: "AC-PAY-001",
    artifact_type: "acceptance_criteria",
    title: "Payment criteria",
    domain: "payments",
    status: "approved",
    version: "1.0",
    text: "Given a valid cart, then the order is paid.",
    frontmatter: {},
    related_openapi_operations: ["createPayment"],
  },
  incidents: [
    {
      document_id: "INC-PAY-001",
      artifact_type: "incident_note",
      title: "Duplicate retry",
      domain: "payments",
      status: "closed",
      version: "1.0",
      text: "Timeout retry duplicated a payment.",
      frontmatter: {},
      related_openapi_operations: ["createPayment"],
    },
  ],
  openapi_operations: [
    {
      operation_id: "createPayment",
      method: "POST",
      path: "/payments",
      parameters: [],
      responses: { "201": { description: "Created" } },
      security: [],
      tags: ["payments"],
      related_schema_names: ["Payment"],
    },
  ],
  related_schemas: [],
  diagrams: [
    {
      diagram_id: "D-PAY-001",
      feature_id: "checkout-payment",
      title: "Payment sequence",
      diagram_type: "sequence",
      source: "@startuml\n@enduml",
      rendered_svg: "<svg><text>Payment</text></svg>",
      related_operation_ids: ["createPayment"],
      steps: [
        {
          step_id: "S1",
          label: "Submit payment",
          related_operation_id: "createPayment",
        },
      ],
    },
  ],
};

const audit: FeatureAuditResult = {
  review_id: "review-1",
  feature_id: "checkout-payment",
  overall_status: "warnings",
  findings: [finding],
  generated_test_ideas: [
    {
      test_id: "test-1",
      title: "Retry timeout",
      type: "regression",
      related_operation_ids: ["createPayment"],
      given_when_then: "Given a timeout, when retried, then the payment is not duplicated.",
      rationale: "Incident coverage.",
    },
  ],
  recommended_next_actions: ["Add retry coverage."],
  model_context_hint: "Check timeout handling.",
};

test("workspaceFromToolResult extracts render payload from structured content and _meta", () => {
  const result: ToolResult = {
    structuredContent: {
      workspace: {
        template_uri: "ui://widget/feature-review-workspace-v1.html",
        view: "overview",
        feature_id: "checkout-payment",
        feature_title: "Checkout Payment",
        feature_count: 1,
        finding_count: 1,
        status: "warnings",
      },
    },
    _meta: {
      features: [
        {
          feature_id: "checkout-payment",
          title: "Checkout Payment",
          domain: "payments",
          user_story_id: "US-PAY-001",
          related_operations_count: 1,
          diagram_count: 1,
          incident_count: 1,
        },
      ],
      context,
      audit,
    },
  };

  const workspace = workspaceFromToolResult(result);

  assert.equal(workspace.workspace?.view, "overview");
  assert.equal(workspace.features[0].feature_id, "checkout-payment");
  assert.equal(workspace.context?.diagrams[0].rendered_svg, "<svg><text>Payment</text></svg>");
  assert.equal(workspace.audit?.findings[0].finding_id, "finding-1");
});

test("contextFromResult reads full context from nested tool metadata", () => {
  const result: ToolResult = {
    structuredContent: { feature_id: "checkout-payment" },
    _meta: {
      mcp_tool_result: {
        _meta: {
          full_context: context,
        },
      },
    },
  };

  assert.equal(contextFromResult(result)?.feature_id, "checkout-payment");
});

test("buildFindingPrompt includes evidence, operation ids, and recommended action", () => {
  const prompt = buildFindingPrompt(finding, context);

  assert.match(prompt, /Checkout Payment/);
  assert.match(prompt, /D-PAY-001, createPayment/);
  assert.match(prompt, /Add the operation marker/);
});

test("sanitizeSvg removes script and event handlers", () => {
  const svg = sanitizeSvg(
    '<svg onload="alert(1)"><script>alert(1)</script><a href="javascript:bad()">x</a><text>ok</text></svg>',
  );

  assert.doesNotMatch(svg, /script/);
  assert.doesNotMatch(svg, /onload/);
  assert.doesNotMatch(svg, /javascript:/);
  assert.match(svg, /<text>ok<\/text>/);
});

test("traceabilityRows maps docs, diagram steps, operations, incidents, and tests", () => {
  const rows = traceabilityRows(context, audit);

  assert.equal(rows.length, 1);
  assert.deepEqual(rows[0], {
    userStory: "US-PAY-001",
    acceptanceCriteria: "AC-PAY-001",
    diagramStep: "S1: Submit payment",
    operationId: "createPayment",
    incident: "INC-PAY-001",
    testIdea: "test-1",
  });
});
