import type { ReviewServiceClient } from "../src/clients/review_service_client.js";
import type {
  FeatureAuditResult,
  FeatureContext,
  FeatureDiagram,
  FeatureSummary,
  IncidentImpactResponse,
  OpenApiOperationSlice,
  ProductDoc,
  TestGapReportResponse,
} from "../src/types.js";

export const featureSummary: FeatureSummary = {
  feature_id: "checkout-payment",
  title: "Checkout Payment",
  domain: "payments",
  user_story_id: "US-PAY-001",
  acceptance_criteria_id: "AC-PAY-001",
  related_operations_count: 1,
  diagram_count: 1,
  incident_count: 1,
  review_status: "warnings",
};

export const userStory: ProductDoc = {
  document_id: "US-PAY-001",
  artifact_type: "user_story",
  title: "Pay for an order",
  domain: "payments",
  status: "approved",
  version: "1.0",
  text: "As a shopper, I can pay for an order using a saved payment method.",
  frontmatter: { feature_id: "checkout-payment" },
  related_openapi_operations: ["createPayment"],
  path: "user_stories/pay_for_order.md",
  related_diagrams: ["D-PAY-001"],
};

export const acceptanceCriteria: ProductDoc = {
  document_id: "AC-PAY-001",
  artifact_type: "acceptance_criteria",
  title: "Payment acceptance criteria",
  domain: "payments",
  status: "approved",
  version: "1.0",
  text: "Given a valid cart, when the shopper submits payment, then the order is paid.",
  frontmatter: { feature_id: "checkout-payment" },
  related_openapi_operations: ["createPayment"],
  path: "acceptance_criteria/payment.md",
  related_user_story: "US-PAY-001",
  related_diagrams: ["D-PAY-001"],
};

export const incident: ProductDoc = {
  document_id: "INC-PAY-001",
  artifact_type: "incident_note",
  title: "Payment timeout retries",
  domain: "payments",
  status: "closed",
  version: "1.0",
  text: "Payment provider timeouts caused duplicate retry attempts.",
  frontmatter: { feature_id: "checkout-payment" },
  related_openapi_operations: ["createPayment"],
  path: "incidents/payment_timeout.md",
  related_user_story: "US-PAY-001",
};

export const operation: OpenApiOperationSlice = {
  operation_id: "createPayment",
  method: "POST",
  path: "/payments",
  summary: "Create a payment",
  description: "Creates a payment authorization for an order.",
  parameters: [],
  request_body: {
    content: {
      "application/json": {
        schema: { $ref: "#/components/schemas/CreatePaymentRequest" },
      },
    },
  },
  responses: {
    "201": {
      description: "Payment created",
    },
  },
  security: [{ bearerAuth: [] }],
  tags: ["payments"],
  related_schema_names: ["CreatePaymentRequest", "Payment"],
};

export const diagram: FeatureDiagram = {
  diagram_id: "D-PAY-001",
  feature_id: "checkout-payment",
  title: "Checkout payment sequence",
  diagram_type: "sequence",
  source: "@startuml\nShopper -> API: POST /payments <<createPayment>>\n@enduml",
  rendered_svg: "<svg role=\"img\"><text>Checkout payment sequence</text></svg>",
  related_operation_ids: ["createPayment"],
  steps: [
    {
      step_id: "S1",
      label: "Submit payment",
      source_line: 2,
      related_operation_id: "createPayment",
      related_path: "/payments",
    },
  ],
  path: "diagrams/payment_sequence.puml",
};

export const featureContext: FeatureContext = {
  feature_id: "checkout-payment",
  title: "Checkout Payment",
  domain: "payments",
  user_story: userStory,
  acceptance_criteria: acceptanceCriteria,
  incidents: [incident],
  openapi_operations: [operation],
  related_schemas: [
    {
      name: "Payment",
      type: "object",
      properties: { id: { type: "string" } },
    },
  ],
  diagrams: [diagram],
};

export const audit: FeatureAuditResult = {
  review_id: "review-checkout-payment",
  feature_id: "checkout-payment",
  overall_status: "warnings",
  findings: [
    {
      finding_id: "finding-retry-timeout",
      severity: "medium",
      category: "incident_coverage",
      title: "Timeout retry coverage is incomplete",
      description: "Acceptance criteria mention payment creation but not provider timeout retries.",
      evidence_refs: ["AC-PAY-001", "INC-PAY-001"],
      affected_operation_ids: ["createPayment"],
      recommended_action: "Add timeout retry acceptance criteria and contract tests.",
    },
  ],
  generated_test_ideas: [
    {
      test_id: "test-payment-timeout",
      title: "Provider timeout does not duplicate payment",
      type: "regression",
      related_operation_ids: ["createPayment"],
      given_when_then:
        "Given the provider times out, when payment is retried, then the same order is not double charged.",
      rationale: "Incident notes identify duplicate retries as a past production issue.",
    },
  ],
  recommended_next_actions: ["Document retry behavior for createPayment."],
  model_context_hint: "Review payment retry and timeout consistency.",
};

export const incidentImpact: IncidentImpactResponse = {
  incident_id: "INC-PAY-001",
  incident,
  related_feature_ids: ["checkout-payment"],
  findings: audit.findings,
  generated_test_ideas: audit.generated_test_ideas,
  model_context_hint: "Incident impacts checkout-payment retry behavior.",
};

export const testGapReport: TestGapReportResponse = {
  feature_id: "checkout-payment",
  findings: audit.findings,
  generated_test_ideas: audit.generated_test_ideas,
  model_context_hint: "Add regression coverage for provider timeouts.",
};

export class FakeReviewServiceClient implements ReviewServiceClient {
  async listFeatures(): Promise<FeatureSummary[]> {
    return [featureSummary];
  }

  async getFeatureContext(): Promise<FeatureContext> {
    return featureContext;
  }

  async getFeatureDiagrams(): Promise<FeatureDiagram[]> {
    return [diagram];
  }

  async getDiagram(): Promise<FeatureDiagram> {
    return diagram;
  }

  async getOpenApiOperation(): Promise<OpenApiOperationSlice> {
    return operation;
  }

  async auditFeatureConsistency(): Promise<FeatureAuditResult> {
    return audit;
  }

  async auditDiagramConsistency(): Promise<FeatureAuditResult> {
    return audit;
  }

  async analyzeIncidentImpact(): Promise<IncidentImpactResponse> {
    return incidentImpact;
  }

  async generateTestGapReport(): Promise<TestGapReportResponse> {
    return testGapReport;
  }
}
