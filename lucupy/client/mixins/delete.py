"""Delete mixins for soft-deleting GraphQL resources.

These mixins provide batch and single-resource deletion functionality,
including support for program ID–scoped deletion.
"""

__all__ = ["DeleteBatchMixin", "DeleteByIdViaBatchMixin", "DeleteBatchByProgramIdMixin"]

from typing import Any, Optional

from .utils import create_program_id_filter

# TODO: Write a _delete_by_id.


async def _delete_batch(
    *,
    client: Any,
    query: str,
    where: dict[str, Any],
    limit: int = 100,
    include_deleted: bool = False,
) -> dict[str, Any]:
    """Helper function to perform a batch soft-delete.

    Parameters
    ----------
    client : `Any`
        The GraphQL client instance.
    query : `str`
        The mutation query template.
    where : `dict[str, Any]`
        Filter to match resources to delete.
    limit : `int`, default=100
        Maximum number of resources to delete.
    include_deleted : `bool`, default=False
        Whether to include already deleted resources.

    Returns
    -------
    `dict[str, Any]`
        The GraphQL response with updated resources.
    """
    input_data = {
        "SET": {"existence": "DELETED"},
        "WHERE": where,
        "LIMIT": limit,
        "includeDeleted": include_deleted,
    }
    return await client._execute(query=query, variables={"input": input_data})


class DeleteBatchMixin:
    """Mixin to soft-delete multiple resources using a custom filter."""

    async def delete_batch(
        self,
        *,
        where: dict[str, Any],
        limit: int = 100,
        include_deleted: bool = False,
        fields: Optional[str] = None,
    ) -> dict[str, Any]:
        """Soft-delete multiple resources using a custom `where` filter.

        Parameters
        ----------
        where : `dict[str, Any]`
            The filter to match resources.
        limit : `int`, default=100
            Maximum number of resources to delete.
        include_deleted : `bool`, default=False
            Whether to include deleted resources in the match.
        fields : `str`, optional
            Optional GraphQL fields to return after deletion.

        Returns
        -------
        `dict[str, Any]`
            The response from the delete mutation.
        """
        client = self.get_client()
        query = self.get_query(query_id="delete_batch", fields=fields)
        return await _delete_batch(
            client=client,
            query=query,
            where=where,
            limit=limit,
            include_deleted=include_deleted,
        )


class DeleteByIdViaBatchMixin:
    """Mixin to soft-delete a resource by ID using batch mutation."""

    async def delete_by_id(
        self,
        *,
        resource_id: str,
        fields: Optional[str] = None,
    ) -> dict[str, Any]:
        """Soft-delete a single resource by its ID.

        Parameters
        ----------
        resource_id : `str`
            ID of the resource to delete.
        fields : `str`, optional
            Optional fields to return after deletion.

        Returns
        -------
        `dict[str, Any]`
            The response from the delete mutation.
        """
        client = self.get_client()
        query = self.get_query(query_id="delete_by_id", fields=fields)
        return await _delete_batch(
            client=client, query=query, where={"id": {"EQ": resource_id}}, limit=1
        )


class DeleteBatchByProgramIdMixin:
    """Mixin to soft-delete resources filtered by program ID."""

    async def delete_batch_by_program_id(
        self,
        *,
        program_id: str,
        where: Optional[dict[str, Any]] = None,
        limit: int = 100,
        include_deleted: bool = False,
        fields: Optional[str] = None,
    ) -> dict[str, Any]:
        """Soft-delete resources associated with a program ID.

        Parameters
        ----------
        program_id : `str`
            The program ID to scope the deletion.
        where : `dict[str, Any]`, optional
            Additional filters to apply.
        limit : `int`, default=100
            Maximum number of resources to delete.
        include_deleted : `bool`, default=False
            Whether to include already deleted resources.
        fields : `str`, optional
            Optional fields to return after deletion.

        Returns
        -------
        `dict[str, Any]`
            The response from the delete mutation.
        """
        client = self.get_client()
        query = self.get_query(query_id="delete_batch_by_program_id", fields=fields)
        program_filter = create_program_id_filter(program_id)

        if where:
            combined_where = {"AND": [program_filter, where]}
        else:
            combined_where = program_filter

        return await _delete_batch(
            client=client,
            query=query,
            where=combined_where,
            limit=limit,
            include_deleted=include_deleted,
        )
