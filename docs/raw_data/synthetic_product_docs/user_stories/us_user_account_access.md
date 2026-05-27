---
document_id: us_user_account_access_v1
artifact_type: user_story
domain: user
status: active
version: v1
related_openapi_operations:
  - createUser
  - createUsersWithListInput
  - loginUser
  - logoutUser
  - getUserByName
  - updateUser
  - deleteUser
related_paths:
  - POST /user
  - POST /user/createWithList
  - GET /user/login
  - GET /user/logout
  - GET /user/{username}
  - PUT /user/{username}
  - DELETE /user/{username}
related_schemas:
  - User
  - Error
---

# User Story: User Account Access

As a store user, I want to create an account, log in, retrieve my profile, update it, and log out so that I can manage my Petstore identity.

## Business Context

User identity is needed for personalized store interactions, support workflows, and administrative account maintenance. The OpenAPI contract exposes user creation, list creation, login/logout, lookup, update, and deletion operations.

## User Goals

- Create a user profile.
- Create multiple users in one request when onboarding test data.
- Log in with username and password query parameters.
- Retrieve a user by username.
- Update or delete a user profile by username.
- Log out of the current session.

## API Touchpoints

- `POST /user` with operationId `createUser` creates one user.
- `POST /user/createWithList` with operationId `createUsersWithListInput` creates users from an array.
- `GET /user/login` with operationId `loginUser` logs a user in.
- `GET /user/logout` with operationId `logoutUser` logs out the current session.
- `GET /user/{username}` with operationId `getUserByName` returns user details.
- `PUT /user/{username}` with operationId `updateUser` updates a user.
- `DELETE /user/{username}` with operationId `deleteUser` deletes a user.

## Product Rules

- `loginUser` accepts `username` and `password` as query parameters.
- Successful login may return `X-Rate-Limit` and `X-Expires-After` response headers.
- User lookup, update, and deletion use `username` as a required path parameter.

## Open Questions

- Should password be sent as a query parameter in a production-ready API?
- Should user deletion require authentication?
- Should `userStatus` have an enum instead of an unrestricted integer?

