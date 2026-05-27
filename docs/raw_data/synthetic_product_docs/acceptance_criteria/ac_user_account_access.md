---
document_id: ac_user_account_access_v1
artifact_type: acceptance_criteria
domain: user
status: active
version: v1
related_user_story: us_user_account_access_v1
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

# Acceptance Criteria: User Account Access

## AC1: Create User

Given a valid `User` payload  
When the request is sent to `POST /user`  
Then the API returns a successful operation response with a `User` representation.

## AC2: Create Users with List

Given a valid array of `User` objects  
When the request is sent to `POST /user/createWithList`  
Then the API returns a successful operation response.

## AC3: Login User

Given a caller provides `username` and `password` query parameters  
When the request is sent to `GET /user/login`  
Then the API returns a successful operation response with a string body.

## AC4: Login Headers

Given login succeeds  
When the response is returned from `GET /user/login`  
Then the response may include `X-Rate-Limit` and `X-Expires-After` headers as documented.

## AC5: Get User by Username

Given a valid `username` path parameter  
When the request is sent to `GET /user/{username}`  
Then the API returns the matching `User`.

## AC6: Update User

Given a valid `username` path parameter and user payload  
When the request is sent to `PUT /user/{username}`  
Then the API returns a successful operation response.

## AC7: Delete User

Given a valid `username` path parameter  
When the request is sent to `DELETE /user/{username}`  
Then the API returns `200 User deleted`.

