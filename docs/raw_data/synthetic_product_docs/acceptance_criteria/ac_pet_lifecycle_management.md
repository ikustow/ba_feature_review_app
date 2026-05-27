---
document_id: ac_pet_lifecycle_management_v1
artifact_type: acceptance_criteria
domain: pet
status: active
version: v1
related_user_story: us_pet_lifecycle_management_v1
related_openapi_operations:
  - addPet
  - updatePet
  - getPetById
  - findPetsByStatus
  - deletePet
related_paths:
  - POST /pet
  - PUT /pet
  - GET /pet/{petId}
  - GET /pet/findByStatus
  - DELETE /pet/{petId}
related_schemas:
  - Pet
---

# Acceptance Criteria: Pet Lifecycle Management

## AC1: Create Pet

Given a catalog manager submits a valid `Pet` payload with `name` and `photoUrls`  
When the request is sent to `POST /pet`  
Then the API returns a successful operation response with a `Pet` representation.

## AC2: Reject Invalid Create Payload

Given a catalog manager submits a pet payload missing required schema fields  
When the request is sent to `POST /pet`  
Then the API returns an error response such as `400 Invalid input` or `422 Validation exception`.

## AC3: Update Existing Pet

Given an existing pet record  
When a valid `Pet` payload is sent to `PUT /pet`  
Then the API updates the pet and returns the updated `Pet` representation.

## AC4: Find Pet by ID

Given a valid `petId` path parameter  
When the request is sent to `GET /pet/{petId}`  
Then the API returns the matching `Pet` record.

## AC5: Handle Missing Pet

Given a valid but unknown `petId`  
When the request is sent to `GET /pet/{petId}`  
Then the API returns `404 Pet not found`.

## AC6: Filter Pets by Status

Given the user filters pets by status  
When the request is sent to `GET /pet/findByStatus` with `status=available`, `status=pending`, or `status=sold`  
Then the API returns only pets matching the requested status value.

## AC7: Delete Pet

Given an authorized caller and a valid `petId`  
When the request is sent to `DELETE /pet/{petId}`  
Then the API returns `200 Pet deleted`.

