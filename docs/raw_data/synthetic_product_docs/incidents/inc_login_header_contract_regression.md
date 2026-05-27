---
document_id: inc_login_header_contract_regression_v1
artifact_type: incident_note
domain: user
status: active
severity: medium
version: v1
related_openapi_operations:
  - loginUser
  - logoutUser
related_paths:
  - GET /user/login
  - GET /user/logout
related_schemas:
  - Error
related_headers:
  - X-Rate-Limit
  - X-Expires-After
---

# Incident Note: Login Header Contract Regression

## Summary

An integration test detected that successful login responses sometimes omitted the `X-Rate-Limit` and `X-Expires-After` headers documented for `GET /user/login`.

## Impact

Client applications that displayed session expiry or rate-limit information could not show accurate account status after login.

## Symptoms

- `GET /user/login` returned `200` with a string body.
- The response body was correct, but one or both documented headers were missing.
- `GET /user/logout` was not affected.

## Suspected Root Cause

The login handler may have been refactored to return the body before applying response header decorators or middleware.

## Affected Contract

- `GET /user/login`
- Response header `X-Rate-Limit`
- Response header `X-Expires-After`

## Resolution Notes

- Add contract tests that assert documented login headers are present on successful responses.
- Keep logout tests separate because the logout operation does not define the same response headers.
- Update client fallback behavior when headers are missing.

## Follow-up Questions

- Are the login headers mandatory or optional in the product contract?
- Should the OpenAPI spec mark these headers as required if clients depend on them?

