---
document_id: inc_pet_status_filter_mismatch_v1
artifact_type: incident_note
domain: pet
status: active
severity: medium
version: v1
related_openapi_operations:
  - findPetsByStatus
  - updatePet
related_paths:
  - GET /pet/findByStatus
  - PUT /pet
related_schemas:
  - Pet
related_fields:
  - Pet.status
---

# Incident Note: Pet Status Filter Mismatch

## Summary

Users reported that filtering pets by `status=available` sometimes returned pets that were already marked as `sold`.

## Impact

Catalog managers could see inaccurate availability lists, which made support workflows slower and increased the risk of showing unavailable pets to customers.

## Symptoms

- `GET /pet/findByStatus?status=available` returned records whose `Pet.status` was `sold`.
- Re-running the same query after an update sometimes produced different results.
- The issue was easier to reproduce after a bulk update through `PUT /pet`.

## Suspected Root Cause

The status filter implementation may have used stale indexed values after pet updates. Another possible cause is inconsistent normalization of the `Pet.status` enum values.

## Affected Contract

- `GET /pet/findByStatus`
- `PUT /pet`
- `Pet.status` enum: `available`, `pending`, `sold`

## Resolution Notes

- Rebuild the status index after each successful pet update.
- Add a regression test that updates `Pet.status` and immediately queries `findPetsByStatus`.
- Verify that only OpenAPI enum values are accepted.

## Follow-up Questions

- Should `findPetsByStatus` support multiple comma-separated statuses or only one value at a time?
- Should invalid status values return `400 Invalid status value` before search is executed?

