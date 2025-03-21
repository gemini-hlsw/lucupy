### How-to use.
Mixins for CRUD operations on GraphQL resource managers.

Each mixin adds one or more methods like `get_by_id`, `delete_batch`, etc.
To use a mixin:
1. Inherit it in your Manager subclass.
2. Add the expected query templates to your `queries` dictionary.
3. Override the method if you want to simplify arguments (like `title`, `text`, etc).

You must provide:
- A `get_client()` method returning your GraphQL client.
- A `get_query(query_id=query_id, fields=fields)` method to inject the selection set.
