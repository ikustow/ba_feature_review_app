export type McpServerConfig = {
  port: number;
  reviewServiceUrl: string;
  publicBaseUrl: string;
};

export function loadConfig(env: NodeJS.ProcessEnv = process.env): McpServerConfig {
  return {
    port: Number(env.PORT ?? 2091),
    reviewServiceUrl: trimTrailingSlash(env.REVIEW_SERVICE_URL ?? "http://127.0.0.1:8000"),
    publicBaseUrl: trimTrailingSlash(env.PUBLIC_BASE_URL ?? "https://feature-review.local"),
  };
}

export function trimTrailingSlash(value: string): string {
  return value.endsWith("/") ? value.slice(0, -1) : value;
}
