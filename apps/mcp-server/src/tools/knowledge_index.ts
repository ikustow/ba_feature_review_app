import type {
  FeatureContext,
  FetchOutput,
  ProductDoc,
  SearchOutput,
} from "./knowledge_types.js";
import type { ReviewServiceClient } from "../clients/review_service_client.js";

type IndexedItem = FetchOutput & {
  haystack: string;
};

export class KnowledgeIndex {
  private items: IndexedItem[] | undefined;

  constructor(
    private readonly client: ReviewServiceClient,
    private readonly publicBaseUrl: string,
  ) {}

  async search(query: string): Promise<SearchOutput> {
    const items = await this.loadItems();
    const terms = query
      .toLowerCase()
      .split(/\s+/)
      .map((term) => term.trim())
      .filter(Boolean);
    const scored = items
      .map((item) => ({
        item,
        score: terms.reduce((sum, term) => sum + (item.haystack.includes(term) ? 1 : 0), 0),
      }))
      .filter(({ score }) => score > 0)
      .sort((left, right) => right.score - left.score || left.item.title.localeCompare(right.item.title))
      .slice(0, 10);

    return {
      results: scored.map(({ item }) => ({
        id: item.id,
        title: item.title,
        url: item.url,
      })),
    };
  }

  async fetch(id: string): Promise<FetchOutput> {
    const items = await this.loadItems();
    const item = items.find((candidate) => candidate.id === id);
    if (!item) {
      throw new Error(`Unknown fetch id: ${id}`);
    }
    const { haystack: _haystack, ...output } = item;
    return output;
  }

  private async loadItems(): Promise<IndexedItem[]> {
    if (this.items) {
      return this.items;
    }

    const features = await this.client.listFeatures();
    const contexts = await Promise.all(
      features.map((feature) => this.client.getFeatureContext(feature.feature_id)),
    );
    this.items = contexts.flatMap((context) => itemsForContext(context, this.publicBaseUrl));
    return this.items;
  }
}

export function itemsForContext(context: FeatureContext, publicBaseUrl: string): IndexedItem[] {
  const items: IndexedItem[] = [];
  items.push(indexedItem(featureItem(context, publicBaseUrl)));
  items.push(indexedItem(docItem(context.user_story, publicBaseUrl)));
  if (context.acceptance_criteria) {
    items.push(indexedItem(docItem(context.acceptance_criteria, publicBaseUrl)));
  }
  for (const incident of context.incidents) {
    items.push(indexedItem(docItem(incident, publicBaseUrl)));
  }
  for (const operation of context.openapi_operations) {
    const item: FetchOutput = {
      id: `operation:${operation.operation_id}`,
      title: `${operation.method} ${operation.path} (${operation.operation_id})`,
      text: JSON.stringify(operation, null, 2),
      url: `${publicBaseUrl}/openapi/operations/${encodeURIComponent(operation.operation_id)}`,
      metadata: {
        source: "openapi_operation",
        operation_id: operation.operation_id,
        feature_id: context.feature_id,
      },
    };
    items.push(indexedItem(item));
  }
  for (const diagram of context.diagrams) {
    const item: FetchOutput = {
      id: `diagram:${diagram.diagram_id}`,
      title: diagram.title,
      text: diagram.source,
      url: `${publicBaseUrl}/diagrams/${encodeURIComponent(diagram.diagram_id)}`,
      metadata: {
        source: "plantuml_diagram",
        diagram_id: diagram.diagram_id,
        feature_id: context.feature_id,
        related_operation_ids: diagram.related_operation_ids,
      },
    };
    items.push(indexedItem(item));
  }
  return items;
}

function featureItem(context: FeatureContext, publicBaseUrl: string): FetchOutput {
  return {
    id: `feature:${context.feature_id}`,
    title: context.title,
    text: [
      `Feature: ${context.title}`,
      `Domain: ${context.domain}`,
      `User story: ${context.user_story.title}`,
      `Acceptance criteria: ${context.acceptance_criteria?.title ?? "none"}`,
      `Operations: ${context.openapi_operations.map((operation) => operation.operation_id).join(", ")}`,
      `Incidents: ${context.incidents.map((incident) => incident.document_id).join(", ") || "none"}`,
    ].join("\n"),
    url: `${publicBaseUrl}/features/${encodeURIComponent(context.feature_id)}`,
    metadata: {
      source: "feature",
      feature_id: context.feature_id,
      domain: context.domain,
    },
  };
}

function docItem(doc: ProductDoc, publicBaseUrl: string): FetchOutput {
  return {
    id: `doc:${doc.document_id}`,
    title: doc.title,
    text: doc.text,
    url: `${publicBaseUrl}/docs/${encodeURIComponent(doc.document_id)}`,
    metadata: {
      source: doc.artifact_type,
      document_id: doc.document_id,
      domain: doc.domain,
      related_openapi_operations: doc.related_openapi_operations,
    },
  };
}

function indexedItem(item: FetchOutput): IndexedItem {
  return {
    ...item,
    haystack: `${item.id} ${item.title} ${item.text} ${JSON.stringify(item.metadata ?? {})}`.toLowerCase(),
  };
}
