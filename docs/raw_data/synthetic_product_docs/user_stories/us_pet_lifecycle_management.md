---
document_id: us_pet_lifecycle_management_v1
artifact_type: user_story
domain: pet
status: active
version: v1
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
  - Category
  - Tag
---

# User Story: Pet Lifecycle Management

As a pet store catalog manager, I want to create, update, find, and remove pet records so that the public catalog reflects the current animals available in the store.

## Business Context

The pet catalog is the primary source used by store staff and customers to understand which pets are available, pending, or sold. The API must support full lifecycle management while preserving accurate status values and searchable metadata.

## User Goals

- Add a new pet with a name and at least one photo URL.
- Update an existing pet when its name, category, tags, photo URLs, or status changes.
- Retrieve a pet by its identifier during support or catalog review.
- Search pets by status to support operational views.
- Delete a pet record when it should no longer appear in the catalog.

## API Touchpoints

- `POST /pet` with operationId `addPet` creates a pet record.
- `PUT /pet` with operationId `updatePet` updates an existing pet.
- `GET /pet/{petId}` with operationId `getPetById` returns one pet.
- `GET /pet/findByStatus` with operationId `findPetsByStatus` lists pets by status.
- `DELETE /pet/{petId}` with operationId `deletePet` removes a pet.

## Product Rules

- `Pet.name` and `Pet.photoUrls` are mandatory because they are required by the `Pet` schema.
- `Pet.status` must use one of the OpenAPI enum values: `available`, `pending`, or `sold`.
- Pet lookup by ID should distinguish invalid IDs from missing pets.
- Delete operations should require authorization through `petstore_auth`.

## Open Questions

- Should `DELETE /pet/{petId}` be a hard delete or a soft delete?
- Should the API prevent direct transitions from `available` to `sold` without an order?
- Should image upload be mandatory before a pet can become `available`?

