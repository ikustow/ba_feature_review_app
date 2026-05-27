---
document_id: us_pet_image_upload_v1
artifact_type: user_story
domain: pet
status: active
version: v1
related_openapi_operations:
  - uploadFile
  - getPetById
  - updatePet
related_paths:
  - POST /pet/{petId}/uploadImage
  - GET /pet/{petId}
  - PUT /pet
related_schemas:
  - ApiResponse
  - Pet
related_security_schemes:
  - petstore_auth
---

# User Story: Pet Image Upload

As a catalog manager, I want to upload an image for a pet so that customers can see accurate visual information before making a store decision.

## Business Context

Pet listings are more useful when they include images. The OpenAPI contract exposes a binary upload operation with optional metadata and a structured API response.

## User Goals

- Upload an image for an existing pet.
- Add optional metadata for the image.
- Receive an upload confirmation through `ApiResponse`.
- Use the pet ID path parameter to associate the image with the correct pet.

## API Touchpoints

- `POST /pet/{petId}/uploadImage` with operationId `uploadFile` uploads a binary image.
- `GET /pet/{petId}` with operationId `getPetById` can verify that the pet exists.
- `PUT /pet` with operationId `updatePet` can update related pet fields after upload.

## Product Rules

- `petId` is a required path parameter.
- `additionalMetadata` is an optional query parameter.
- The request body accepts `application/octet-stream`.
- Upload requires `petstore_auth` with pet read/write scopes.

## Open Questions

- Should file size and media type limits be documented?
- Should the upload endpoint reject image upload for missing pets before reading the binary body?
- Should successful upload update `Pet.photoUrls` automatically?

