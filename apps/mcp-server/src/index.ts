import { HttpReviewServiceClient } from "./clients/review_service_client.js";
import { loadConfig } from "./config.js";
import { createHttpApp } from "./transport/http.js";

const config = loadConfig();
const reviewClient = new HttpReviewServiceClient(config.reviewServiceUrl);
const app = createHttpApp(reviewClient, config);

app.listen(config.port, () => {
  console.log(`Feature Review MCP server listening on http://127.0.0.1:${config.port}/mcp`);
  console.log(`Review service: ${config.reviewServiceUrl}`);
});
