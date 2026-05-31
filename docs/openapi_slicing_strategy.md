# OpenAPI Slicing Strategy

The app never sends the full `docs/raw_data/openapi.yaml` to ChatGPT. Instead, the review service builds compact operation slices for the selected feature.

## Inputs

- Source spec: `docs/raw_data/openapi.yaml`
- Feature manifest: `docs/raw_data/synthetic_product_docs/manifest.json`
- Feature-level `related_openapi_operations`

Example:

```json
{
  "document_id": "us_pet_lifecycle_management_v1",
  "related_openapi_operations": [
    "addPet",
    "updatePet",
    "getPetById",
    "findPetsByStatus",
    "deletePet"
  ]
}
```

## Pipeline

```text
openapi.yaml
  -> parser.py
  -> operation_index.py
  -> slicer.py
  -> schema_resolver.py
  -> FeatureContext.openapi_operations + related_schemas
```

## Operation Index

The index supports lookup by:

- `operationId`
- method + path
- tag
- referenced schema names

The feature catalog primarily uses stable `operationId` values from the manifest.

## Operation Slice Shape

Each selected operation returns only review-relevant fields:

- `method`
- `path`
- `operation_id`
- `summary`
- `description`
- `parameters`
- `request_body`
- `responses`
- `security`
- `tags`
- `related_schema_names`

This is enough for traceability, review, and ChatGPT explanation without flooding the conversation with the full OpenAPI document.

## Schema Resolution

The schema resolver follows `$ref` values only for schemas needed by selected operations. It applies a depth limit to avoid runaway nested references.

Returned schemas are used for deterministic checks such as:

- required fields not mentioned in docs;
- enum values missing from product rules;
- response/documentation coverage gaps.

## Example: Pet Lifecycle Management

Expected operation slice:

```text
POST   /pet               addPet
PUT    /pet               updatePet
GET    /pet/{petId}       getPetById
GET    /pet/findByStatus  findPetsByStatus
DELETE /pet/{petId}       deletePet
```

The slicer should not return unrelated Store or User operations for this feature.

## Validation Checks

Useful tests:

- related operation IDs exist in the OpenAPI spec;
- feature context contains only related operations;
- related schemas are present but `components` is not returned wholesale;
- unknown operation IDs fail clearly;
- schema reference depth is bounded.

## Known Limitations

- The current dataset is small and synthetic.
- Operation matching is based on manifest-provided IDs, not fuzzy natural-language inference.
- Cross-feature dependencies are represented only when the manifest or docs link them explicitly.
