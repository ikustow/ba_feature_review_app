# Architecture

This app keeps the reasoning, data access, and visualization layers deliberately separate.

```text
User
  -> ChatGPT
      -> MCP tools
          -> review-service API
              -> raw product docs
              -> OpenAPI parser/slicer
              -> PlantUML parser/renderer
              -> deterministic checks
      -> widget resource
          -> Feature Review Workspace
```

## Responsibilities

ChatGPT:

- Interprets user intent.
- Chooses the right read-only MCP tools.
- Explains deterministic findings in natural language.
- Answers follow-up questions using tool outputs and evidence.

MCP server:

- Exposes the tool surface to ChatGPT.
- Keeps tool outputs compact.
- Places large widget-only payloads in `_meta`.
- Registers the widget resource with `text/html;profile=mcp-app`.
- Provides standard `search` and `fetch` compatibility.

Review service:

- Loads the synthetic product documentation manifest.
- Parses Markdown frontmatter and bodies.
- Builds feature context from user story, acceptance criteria, incidents, diagrams, and OpenAPI slices.
- Renders PlantUML diagrams to SVG.
- Runs deterministic rule checks.

Widget:

- Shows an inline launcher in ChatGPT.
- Requests fullscreen mode for the full workspace.
- Renders feature list, overview, docs, OpenAPI table, diagram, incidents, findings, test gaps, traceability, and source views.
- Lets users select evidence and ask ChatGPT targeted follow-up questions.

## Data Flow

For a chat-first review prompt such as:

```text
Review Pet Lifecycle Management. Do the user story, acceptance criteria, and OpenAPI slice match?
```

Expected high-level flow:

```text
1. list_features
2. get_feature_context(feature_id)
3. get_feature_diagrams(feature_id)
4. audit_feature_consistency(feature_id)
5. audit_diagram_consistency(feature_id)
6. render_feature_review_workspace(feature_id, view)
7. ChatGPT explains the result
```

The widget can also call read-only tools directly through `window.openai.callTool` when the user selects a feature.

## Tool Surface

MVP tools:

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

All MVP tools are read-only.

## Widget Resource Strategy

The MCP server registers the React/Vite widget as a versioned resource:

```text
ui://widget/feature-review-workspace-v6.html
```

The URI is treated as the cache key. When widget HTML, CSS, or JS changes in a meaningful way, the URI should be bumped and all references updated.

## Structured Content And Metadata

The tool response split is intentional:

- `structuredContent`: compact fields visible to ChatGPT and the widget.
- `content`: concise text summary for the conversation.
- `_meta`: larger widget-only payloads such as full context, rendered SVG, and audits.

This keeps the model context small while giving the widget enough data to render a rich workspace.

## Read-Only Boundary

The MVP does not edit documentation. User story editing, write-back, GitHub PR creation, or persistent drafts would require a separate mutating tool design and updated annotations.
