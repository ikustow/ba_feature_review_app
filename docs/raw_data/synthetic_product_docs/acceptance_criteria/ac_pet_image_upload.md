---
document_id: ac_pet_image_upload_v1
artifact_type: acceptance_criteria
domain: pet
status: active
version: v1
related_user_story: us_pet_image_upload_v1
related_openapi_operations:
  - uploadFile
  - getPetById
related_paths:
  - POST /pet/{petId}/uploadImage
  - GET /pet/{petId}
related_schemas:
  - ApiResponse
  - Error
related_security_schemes:
  - petstore_auth
---

# Acceptance Criteria: Pet Image Upload

## AC1: Upload Pet Image

Given an existing pet and a binary image payload  
When the request is sent to `POST /pet/{petId}/uploadImage`  
Then the API returns a successful operation response with `ApiResponse`.

## AC2: Optional Metadata

Given the caller includes `additionalMetadata`  
When the image upload request is processed  
Then the metadata is accepted as an optional query parameter.

## AC3: Missing File

Given the caller sends no binary file  
When the request is sent to `POST /pet/{petId}/uploadImage`  
Then the API returns `400 No file uploaded`.

## AC4: Missing Pet

Given the caller uses a `petId` that does not exist  
When the image upload request is processed  
Then the API returns `404 Pet not found`.

## AC5: Authorization

Given the caller uploads a pet image  
When the request is sent to the upload endpoint  
Then the caller must satisfy `petstore_auth` with pet read/write scopes.

