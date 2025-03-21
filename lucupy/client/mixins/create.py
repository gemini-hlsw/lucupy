"""Create mixin for GraphQL resources.

This module provides functionality to create new resources using a standard
GraphQL `create` mutation pattern.
"""

__all__ = ["CreateMixin"]

from typing import Any, Optional


async def _create(
    *, client: Any, query: str, set_values: dict[str, Any]
) -> dict[str, Any]:
    """Helper to perform a create mutation.

    Parameters
    ----------
    client : `Any`
        The GraphQL client instance.
    query : `str`
        The GraphQL mutation string with `{fields}` already substituted.
    set_values : `dict[str, Any]`
        The input data to send as the `SET` payload.

    Returns
    -------
    `dict[str, Any]`
        The GraphQL response for the newly created resource.
    """
    input_data: dict[str, Any] = {"SET": set_values}

    return await client._execute(query=query, variables={"input": input_data})


class CreateMixin:
    """Mixin to create a new resource using a GraphQL mutation."""

    async def create(
        self, *, set_values: dict[str, Any], fields: Optional[str] = None
    ) -> dict[str, Any]:
        """Create a new resource via a GraphQL mutation.

        Parameters
        ----------
        set_values : `dict[str, Any]`
            The fields to include in the new resource.
        fields : `str`, optional
            Optional fields to return in the mutation response. Defaults to `default_fields`.

        Returns
        -------
        `dict[str, Any]`
            The GraphQL response for the newly created resource.
        """
        client = self.get_client()
        query = self.get_query(query_id="create", fields=fields)

        return await _create(client=client, query=query, set_values=set_values)
