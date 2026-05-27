# AGENTS.MD

## Project

This repo is for **Project 3: AI Feature Review ChatGPT App**.

The app is a read-only ChatGPT App that reviews feature documentation across:

- product docs;
- acceptance criteria;
- incident notes;
- PlantUML feature diagrams;
- OpenAPI operation slices.

Core architecture:

```text
ChatGPT = reasoning layer
MCP/backend = deterministic data access, OpenAPI slicing, diagram loading/rendering, traceability, rule checks
Widget = Feature Review Workspace
```

Do not add a backend AI/LangChain/LangGraph layer for MVP unless the PRD is explicitly changed.

## Start Here

Read these first before implementation:

- `PRD/project_3_ai_business_analyst_copilot.md` - product concept and architecture.
- `PRD/project_3_feature_review_app_development_plan.md` - step-by-step build plan and MVP checklist.
- `docs/raw_data/openapi.yaml` - source OpenAPI spec.
- `docs/raw_data/synthetic_product_docs/manifest.json` - expected dataset manifest once present/updated.

Current raw data may be incomplete relative to the PRD. The plan expects adding:

```text
docs/raw_data/synthetic_product_docs/
  manifest.json
  user_stories/
  acceptance_criteria/
  incidents/
  diagrams/*.puml
```

## OpenAI / Apps SDK Guidance

When implementing or changing the ChatGPT App/MCP layer, use the OpenAI docs skills first:

- `openai-docs` - fetch current official OpenAI docs.
- `openai-developers:build-chatgpt-app` - Apps SDK / MCP server / widget patterns.
- `openai-developers:openai-api-troubleshooting` - only if OpenAI API calls fail.
- `openai-developers:openai-platform-api-key` - only if a task actually requires an OpenAI API key.

Relevant official docs to check:

- `https://developers.openai.com/apps-sdk/quickstart/`
- `https://developers.openai.com/apps-sdk/build/mcp-server/`
- `https://developers.openai.com/apps-sdk/build/chatgpt-ui/`
- `https://developers.openai.com/apps-sdk/plan/tools/`
- `https://developers.openai.com/apps-sdk/reference/`
- `https://developers.openai.com/apps-sdk/deploy/connect-chatgpt`

## MVP Rules

- All MVP tools are read-only.
- Do not implement document mutation, apply changes, PR creation, or write-back flows.
- Do not send the full `openapi.yaml` to ChatGPT; return feature-specific operation slices.
- Keep tool outputs structured and compact.
- Put large widget-only payloads in `_meta`.
- Keep `search` and `fetch` compatible with the standard company-knowledge shape.
- Use PlantUML `.puml` diagrams as source and render them as SVG for the widget.

## Expected Tool Surface

MCP tools planned for MVP:

- `list_features`
- `get_feature_context`
- `get_openapi_operation`
- `get_feature_diagrams`
- `get_diagram`
- `audit_feature_consistency`
- `audit_diagram_consistency`
- `analyze_incident_impact`
- `generate_test_gap_report`
- `render_feature_review_workspace`
- `search`
- `fetch`

## Local Dev Loop

Expected local flow:

```bash
# review service
cd services/review-service
uv run uvicorn feature_review.api.main:app --reload --port 8000

# MCP server
cd apps/mcp-server
pnpm dev

# tunnel for ChatGPT Developer Mode
ngrok http 2091
```

Connect ChatGPT Developer Mode to:

```text
https://<subdomain>.ngrok.app/mcp
```

## Testing Priorities

Prioritize tests for:

- manifest loading;
- markdown/frontmatter parsing;
- OpenAPI operation indexing;
- OpenAPI slicing;
- schema ref resolution;
- PlantUML loading/parsing/rendering;
- diagram step -> operationId mapping;
- deterministic rule checks;
- MCP tool output contracts;
- `search`/`fetch` compatibility;
- widget rendering of feature list, diagram view, OpenAPI table, and findings.

## Implementation Notes

- Prefer deterministic parsers and structured data over ad hoc string matching.
- Use YAML/OpenAPI parsing libraries for `openapi.yaml`.
- Use stable IDs from manifest/docs everywhere.
- Keep evidence refs in findings: document IDs, operation IDs, schema names, diagram IDs.
- Use React/Vite/TypeScript for the widget unless PRD changes.
- Use FastAPI/Pydantic for the review backend unless PRD changes.
