# Evaluation Methodology

The app should be evaluated as a deterministic context and visualization layer for ChatGPT, not as a standalone AI reviewer.

## Goals

The MVP is successful when:

- ChatGPT can discover the right feature from user wording.
- Tool outputs contain enough structured context for grounded explanations.
- OpenAPI context is feature-specific and compact.
- Findings are deterministic and evidence-backed.
- Widget views make the evidence inspectable.
- ChatGPT does not invent endpoints, incidents, diagrams, or requirements.

## Evaluation Scenarios

Manual scenarios:

1. Chat-first feature review.
2. App-first feature selection.
3. Diagram flow inspection.
4. Operation-level OpenAPI question.
5. Incident impact analysis.
6. QA gap report.
7. Finding follow-up through the widget.

## Expected Properties

For every answer:

- Names the feature being reviewed.
- References actual document IDs, operation IDs, schema names, diagram IDs, or incident IDs where relevant.
- Distinguishes deterministic findings from suggested interpretation.
- Avoids unrelated OpenAPI operations.
- Avoids claiming source docs were edited.
- Keeps MVP read-only.

## Metrics

Recommended lightweight scoring:

| Property | Pass condition |
| --- | --- |
| Feature selection | Correct feature ID is used or ambiguity is clarified. |
| OpenAPI scope | Only related operations are returned for feature context. |
| Evidence grounding | Findings include stable evidence refs. |
| Diagram linking | Diagram steps map to operation IDs where markers exist. |
| No hallucinated endpoints | Answer uses only operations present in the slice. |
| Read-only behavior | No save, mutation, PR, or write-back action is offered as completed. |
| Widget usability | Feature list, diagram, OpenAPI table, and findings render without blank states. |

## Suggested Test Prompts

```text
Review Pet Lifecycle Management. Do the user story, acceptance criteria, and OpenAPI slice match?
```

```text
What is wrong around findPetsByStatus?
```

```text
Create a QA gap report for Store Order Checkout.
```

```text
Show the diagram flow for User Account Access and list the operationIds on the diagram.
```

```text
Which requirements are not covered by the acceptance criteria for Pet Image Upload?
```

## Negative Checks

The app should not:

- return the full `openapi.yaml`;
- invent operation IDs;
- treat synthetic docs as private production material;
- claim to update Markdown docs;
- create GitHub PRs;
- hide deterministic evidence behind prose only;
- require a backend AI service.

## Regression Checklist

Before recording a demo:

- `list_features` returns 4 features.
- Widget resource loads with the current versioned URI.
- Inline launcher opens in ChatGPT.
- Fullscreen workspace opens from the launcher.
- Diagram SVG is non-empty and readable.
- OpenAPI table shows related operations only.
- `Ask ChatGPT` produces a follow-up grounded in selected evidence.
- Tests pass for backend, MCP, and widget contracts.
