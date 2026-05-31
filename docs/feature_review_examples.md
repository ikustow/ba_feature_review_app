# Feature Review Examples

This document provides demo-ready examples for portfolio narration and manual validation.

## Example 1: Pet Lifecycle Management

Prompt:

```text
Review Pet Lifecycle Management. Do the user story, acceptance criteria, and OpenAPI slice match?
```

Expected tool path:

```text
list_features
get_feature_context(us_pet_lifecycle_management_v1)
audit_feature_consistency(us_pet_lifecycle_management_v1)
audit_diagram_consistency(us_pet_lifecycle_management_v1)
render_feature_review_workspace(us_pet_lifecycle_management_v1)
```

Feature context should include:

- user story `us_pet_lifecycle_management_v1`;
- acceptance criteria `ac_pet_lifecycle_management_v1`;
- incident `inc_pet_status_filter_mismatch_v1`;
- diagram `diag_pet_lifecycle_sequence_v1`;
- operation slice for `addPet`, `updatePet`, `getPetById`, `findPetsByStatus`, and `deletePet`.

Expected review themes:

- error response coverage needs documentation;
- required schema fields are not fully reflected in docs;
- update-then-filter regression coverage is needed around `updatePet` and `findPetsByStatus`;
- open questions remain in the story or incident note.

## Example 2: Incident Impact

Prompt:

```text
What does the Pet Status Filter Mismatch incident tell us about missing tests?
```

Expected behavior:

- ChatGPT identifies the incident as related to `findPetsByStatus` and `updatePet`.
- The app surfaces regression test ideas.
- The widget provides evidence from the incident, related docs, and operation IDs.

Good concise answer shape:

```text
The incident suggests a regression gap around updating a pet status and immediately verifying that status through findPetsByStatus. Add a regression test that updates status through updatePet, searches by the new status, and verifies the pet appears exactly once.
```

## Example 3: Store Order Checkout QA Gap Report

Prompt:

```text
Create a QA gap report for Store Order Checkout.
```

Feature context should include:

- `placeOrder`
- `getOrderById`
- `deleteOrder`
- `getInventory`
- incident `inc_order_id_boundary_confusion_v1`
- diagram `diag_store_order_checkout_sequence_v1`

Expected review themes:

- order ID boundary behavior needs operation-specific tests;
- error responses need clearer documentation;
- required fields and schema expectations need stronger coverage.

## Example 4: User Account Access

Prompt:

```text
Review User Account Access and explain the risks around login/logout.
```

Expected review themes:

- login header contract needs explicit regression coverage;
- secured/session-related behavior should be tied to docs and tests;
- user operations should remain scoped to the feature's OpenAPI slice.

## Example 5: Pet Image Upload

Prompt:

```text
Review Pet Image Upload. Which requirements are not covered by the acceptance criteria?
```

Expected review themes:

- acceptance criteria miss some feature operations;
- error response coverage is incomplete;
- required schema fields and enum values need clearer product rules.

## Demo Recording Storyboard

1. Start with the inline launcher.
2. Open fullscreen workspace.
3. Select `Pet Lifecycle Management`.
4. Show the diagram tab and operation-linked steps.
5. Switch to OpenAPI and show only related operations.
6. Switch to Consistency and show evidence-backed findings.
7. Click "Ask ChatGPT" on a finding.
8. Show ChatGPT answering with evidence IDs and operation IDs.

Use the GIF slots listed in the root README for the final portfolio page.
