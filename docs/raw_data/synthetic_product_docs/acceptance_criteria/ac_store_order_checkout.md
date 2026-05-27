---
document_id: ac_store_order_checkout_v1
artifact_type: acceptance_criteria
domain: store
status: active
version: v1
related_user_story: us_store_order_checkout_v1
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

# Acceptance Criteria: Store Order Checkout

## AC1: Place Order

Given a customer submits an `Order` payload  
When the request is sent to `POST /store/order`  
Then the API returns a successful operation response with an `Order` representation.

## AC2: Reject Invalid Order

Given a customer submits an invalid order payload  
When the request is sent to `POST /store/order`  
Then the API returns `400 Invalid input` or `422 Validation exception`.

## AC3: Retrieve Order by ID

Given an order exists and the caller provides a valid `orderId`  
When the request is sent to `GET /store/order/{orderId}`  
Then the API returns the matching `Order`.

## AC4: Handle Missing Order

Given an order does not exist  
When the request is sent to `GET /store/order/{orderId}`  
Then the API returns `404 Order not found`.

## AC5: Delete Order

Given an order can be deleted  
When the request is sent to `DELETE /store/order/{orderId}`  
Then the API returns `200 order deleted`.

## AC6: Inventory Requires API Key

Given a caller requests inventory counts  
When the request is sent to `GET /store/inventory`  
Then the request must include the `api_key` security scheme.

