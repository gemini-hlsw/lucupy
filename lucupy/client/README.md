# GPP GraphQL Client

This library provides an ergonomic, extensible GraphQL client for interacting with the Gemini Program Platform (GPP) API. It is designed with developer experience in mind—offering a clean structure, reusable mixins, and strongly typed manager patterns to help both library authors and users work with the GPP schema effectively.

## Overview

The client follows a resource manager pattern. Each manager encapsulates the logic and operations for a specific GraphQL resource, such as program notes or observations. Reusable behavior is implemented via mixins, making it easy to compose managers and override only what's necessary.

## Philosophy

### Why mixins?

GraphQL operations across many resources share the same structure: create, get, update, delete, and restore. Mixins abstract that shared logic while still allowing customization at the manager level (e.g., `ProgramNoteManager`) for more ergonomic public APIs.

### Why managers?

Each resource gets a dedicated manager that acts as a namespace for operations and ensures consistency. Managers:
- Register query templates and default return fields.
- Compose relevant mixins to define supported operations.
- Optionally override methods to simplify the interface for users (e.g., no need to manually build `set_values`).

### Why is this easy for users?

Users can interact with the API using simple, high-level calls. See `example.ipynb` for a walkthrough. Managers expose intuitive async methods like `create`, `get_by_id`, or `update_by_id`, with sensible defaults. Users can override fields to return only what they need, using raw strings.

## Proof of Concept: `ProgramNoteManager`

The `program_note` resource is fully implemented and serves as a proof of concept. It supports:

- `create`
- `get_by_id`
- `get_batch`
- `update_by_id`
- `delete_by_id`, `delete_batch_by_program_id`, etc.
- Field overrides for any operation via the `{fields}` placeholder in templates

Custom logic is added in `create()` and `update_by_id()` to make them easier to use, building `set_values` for the user automatically.

## Remaining Work

- Implement remaining managers under `managers/`
- Write queries and mutations for each resource
- Add parsing hooks for mapping raw GraphQL responses into minimal client-side data models
- Develop plugin method for attaching new managers developed by users
- Move to own repo and setup testing infrastructure and code formatting

## Goals

- Provide a consistent and minimal abstraction over GPP GraphQL
- Minimize boilerplate when creating new resource managers
- Support field selection overrides to reduce payload size
- Be as easy to use as possible with async/await

## Getting Started
See `example.ipynb` for more full example.

```python
from client import GPPClient

client = GPPClient(url="https://your-gpp-api/graphql", auth_token="abc123")

# Create a program note.
note = await client.program_note.create(
    title="Night Log",
    text="Clear skies. Everything worked as expected.",
    program_id="p-123"
)

# Fetch it by ID.
fetched = await client.program_note.get_by_id(resource_id=note["id"])
```
