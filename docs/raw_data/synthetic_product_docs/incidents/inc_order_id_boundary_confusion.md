---
document_id: inc_order_id_boundary_confusion_v1
artifact_type: incident_note
domain: store
status: active
severity: low
version: v1
related_openapi_operations:
  - getOrderById
  - deleteOrder
related_paths:
  - GET /store/order/{orderId}
  - DELETE /store/order/{orderId}
related_schemas:
  - Order
  - Error
---

# Incident Note: Order ID Boundary Confusion

## Summary

QA reported inconsistent expectations for `orderId` boundary behavior between retrieving and deleting store orders.

## Impact

Test cases failed intermittently because different teams interpreted the documented ID ranges differently.

## Symptoms

- `GET /store/order/{orderId}` documentation says valid responses can be tested with integer IDs `<= 5` or `> 10`.
- `DELETE /store/order/{orderId}` documentation says valid delete behavior can be tested with integer IDs below `1000`.
- Test data with `orderId=1001` created ambiguity between retrieval and deletion scenarios.

## Suspected Root Cause

The OpenAPI descriptions document test-server behavior rather than product behavior. The contract does not define a single shared boundary rule for all order operations.

## Affected Contract

- `GET /store/order/{orderId}`
- `DELETE /store/order/{orderId}`
- `Order.id`
- `Error`

## Resolution Notes

- Keep operation-specific boundary tests separate.
- Add acceptance criteria that explicitly distinguish lookup ID behavior from delete ID behavior.
- Avoid using test IDs around `1000` in shared regression suites unless the operation is specified.

## Follow-up Questions

- Should `orderId` constraints be represented as schema validation rules?
- Should the API return `400 Invalid ID supplied` for all invalid boundary cases?

