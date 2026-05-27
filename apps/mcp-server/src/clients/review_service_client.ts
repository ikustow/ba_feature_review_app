import type {
  FeatureAuditResult,
  FeatureContext,
  FeatureDiagram,
  FeatureSummary,
  IncidentImpactResponse,
  OpenApiOperationSlice,
  TestGapReportResponse,
} from "../types.js";

export interface ReviewServiceClient {
  listFeatures(): Promise<FeatureSummary[]>;
  getFeatureContext(featureId: string): Promise<FeatureContext>;
  getFeatureDiagrams(featureId: string): Promise<FeatureDiagram[]>;
  getDiagram(diagramId: string): Promise<FeatureDiagram>;
  getOpenApiOperation(operationId: string): Promise<OpenApiOperationSlice>;
  auditFeatureConsistency(featureId: string): Promise<FeatureAuditResult>;
  auditDiagramConsistency(featureId: string): Promise<FeatureAuditResult>;
  analyzeIncidentImpact(incidentId: string): Promise<IncidentImpactResponse>;
  generateTestGapReport(featureId: string): Promise<TestGapReportResponse>;
}

export class HttpReviewServiceClient implements ReviewServiceClient {
  constructor(
    private readonly baseUrl: string,
    private readonly fetchImpl: typeof fetch = fetch,
  ) {}

  async listFeatures(): Promise<FeatureSummary[]> {
    const payload = await this.get<{ features: FeatureSummary[] }>("/features");
    return payload.features;
  }

  getFeatureContext(featureId: string): Promise<FeatureContext> {
    return this.get(`/features/${encodeURIComponent(featureId)}`);
  }

  async getFeatureDiagrams(featureId: string): Promise<FeatureDiagram[]> {
    const payload = await this.get<{ diagrams: FeatureDiagram[] }>(
      `/features/${encodeURIComponent(featureId)}/diagrams`,
    );
    return payload.diagrams;
  }

  getDiagram(diagramId: string): Promise<FeatureDiagram> {
    return this.get(`/diagrams/${encodeURIComponent(diagramId)}`);
  }

  getOpenApiOperation(operationId: string): Promise<OpenApiOperationSlice> {
    return this.get(`/openapi/operations/${encodeURIComponent(operationId)}`);
  }

  auditFeatureConsistency(featureId: string): Promise<FeatureAuditResult> {
    return this.post(`/features/${encodeURIComponent(featureId)}/audit`);
  }

  auditDiagramConsistency(featureId: string): Promise<FeatureAuditResult> {
    return this.post(`/features/${encodeURIComponent(featureId)}/diagram-audit`);
  }

  analyzeIncidentImpact(incidentId: string): Promise<IncidentImpactResponse> {
    return this.post(`/incidents/${encodeURIComponent(incidentId)}/impact`);
  }

  generateTestGapReport(featureId: string): Promise<TestGapReportResponse> {
    return this.post(`/features/${encodeURIComponent(featureId)}/test-gaps`);
  }

  private get<T>(path: string): Promise<T> {
    return this.request<T>("GET", path);
  }

  private post<T>(path: string): Promise<T> {
    return this.request<T>("POST", path);
  }

  private async request<T>(method: "GET" | "POST", path: string): Promise<T> {
    const response = await this.fetchImpl(`${this.baseUrl}${path}`, { method });
    if (!response.ok) {
      const body = await response.text();
      throw new Error(`Review service ${method} ${path} failed: ${response.status} ${body}`);
    }
    return (await response.json()) as T;
  }
}
