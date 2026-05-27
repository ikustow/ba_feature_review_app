---
document_id: us_store_order_checkout_v1
artifact_type: user_story
domain: store
status: active
version: v1
related_openapi_operations:
  - placeOrder
  - getOrderById
  - deleteOrder
  - getInventory
related_paths:
  - POST /store/order
  - GET /store/order/{orderId}
  - DELETE /store/order/{orderId}
  - GET /store/inventory
related_schemas:
  - Order
  - Error
related_security_schemes:
  - api_key
---

# User Story: Store Order Checkout

As a store customer, I want to place an order for a pet and later retrieve the purchase order so that I can confirm the order state and delivery progress.

## Business Context

The store order flow connects customer intent with inventory availability. The API must allow order placement, order lookup, and administrative cancellation while keeping order status clear.

## User Goals

- Place an order for a pet using `petId`, `quantity`, and optional shipping details.
- Retrieve an order by `orderId`.
- Delete an order when it is invalid or no longer needed.
- Check inventory quantities grouped by pet status.

## API Touchpoints

- `POST /store/order` with operationId `placeOrder` places a new order.
- `GET /store/order/{orderId}` with operationId `getOrderById` retrieves a purchase order.
- `DELETE /store/order/{orderId}` with operationId `deleteOrder` deletes an order.
- `GET /store/inventory` with operationId `getInventory` returns inventory counts and requires `api_key`.

## Product Rules

- `Order.status` must use one of the OpenAPI enum values: `placed`, `approved`, or `delivered`.
- `GET /store/order/{orderId}` has documented test behavior for IDs with value `<= 5` or `> 10`.
- `DELETE /store/order/{orderId}` has documented test behavior for IDs below `1000`.
- Inventory access requires `api_key`.

## Open Questions

- Should order placement validate that the referenced `petId` exists?
- Should order placement update `Pet.status` from `available` to `pending`?
- Should deleting an order restore inventory or pet status?

