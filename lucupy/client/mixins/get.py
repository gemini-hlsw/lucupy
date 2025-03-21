"""Get mixins for retrieving GraphQL resources by ID or batch.

This module provides reusable mixins to support fetching resources
by ID, by filters, or in batch by program ID using GraphQL queries.
"""

__all__ = ["GetByIdMixin", "GetBatchMixin", "GetBatchByProgramIdMixin"]

from typing import Any, Optional

from .utils import create_program_id_filter


async def _get_by_id(
    *, client: Any, query: str, resource_id: str, resource_id_field: str
) -> dict[str, Any]:
    """Execute a GraphQL query to retrieve a resource by ID.

    Parameters
    ----------
    client : `Any`
        The GraphQL client instance.
    query : `str`
        The query string with a variable placeholder.
    resource_id : `str`
        The ID value to use as a filter.
    resource_id_field : `str`
        The name of the query variable expected by the API.

    Returns
    -------
    `dict[str, Any]`
        The result of the query.
    """
    return await client._execute(
        query=query, variables={f"{resource_id_field}": resource_id}
    )


async def _get_batch(
    *,
    client: Any,
    query: str,
    where: Optional[dict[str, Any]] = None,
    offset: Optional[str] = None,
    limit: int = 100,
    include_deleted: bool = False,
) -> dict[str, Any]:
    """Execute a GraphQL query to retrieve a batch of resources.

    Parameters
    ----------
    client : `Any`
        The GraphQL client instance.
    query : `str`
        The query string for batch retrieval.
    where : `dict[str, Any]`, optional
        Filter expression.
    offset : `str`, optional
        Offset cursor for pagination.
    limit : `int`, default=100
        Maximum number of items to return.
    include_deleted : `bool`, default=False
        Whether to include soft-deleted resources.

    Returns
    -------
    `dict[str, Any]`
        The batch query result.
    """
    return await client._execute(
        query=query,
        variables={
            "where": where,
            "offset": offset,
            "limit": limit,
            "includeDeleted": include_deleted,
        },
    )


class GetByIdMixin:
    """Mixin to fetch a single resource by its ID."""

    async def get_by_id(
        self,
        *,
        resource_id: str,
        fields: Optional[str] = None,
    ) -> dict[str, Any]:
        """Fetch a single resource by its ID.

        Parameters
        ----------
        resource_id : `str`
            The unique ID of the resource to retrieve.
        fields : `str`, optional
            The fields to return in the response.

        Returns
        -------
        `dict[str, Any]`
            The resource data.
        """
        client = self.get_client()
        query = self.get_query(query_id="get_by_id", fields=fields)
        resource_id_field = self.get_resource_id_field()

        return await _get_by_id(
            client=client,
            query=query,
            resource_id=resource_id,
            resource_id_field=resource_id_field,
        )


class GetBatchMixin:
    """Mixin to fetch multiple resources based on filters."""

    async def get_batch(
        self,
        *,
        where: Optional[dict[str, Any]] = None,
        offset: Optional[str] = None,
        limit: int = 100,
        include_deleted: bool = False,
        fields: Optional[str] = None,
    ) -> dict[str, Any]:
        """Fetch a batch of resources using filter expressions.

        Parameters
        ----------
        where : `dict[str, Any]`, optional
            Filter expression to match resources.
        offset : `str`, optional
            Pagination cursor.
        limit : `int`, default=100
            Maximum number of results.
        include_deleted : `bool`, default=False
            Whether to include soft-deleted entries.
        fields : `str`, optional
            The fields to return in the response.

        Returns
        -------
        `dict[str, Any]`
            The batch query result.
        """
        client = self.get_client()
        query = self.get_query(query_id="get_batch", fields=fields)
        return await _get_batch(
            client=client,
            query=query,
            where=where,
            offset=offset,
            limit=limit,
            include_deleted=include_deleted,
        )


class GetBatchByProgramIdMixin:
    """Mixin to fetch multiple resources scoped to a specific program."""

    async def get_batch_by_program_id(
        self,
        *,
        program_id: str,
        where: Optional[dict[str, Any]] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> dict[str, Any]:
        """Fetch a batch of resources linked to a specific program.

        Parameters
        ----------
        program_id : `str`
            The program ID to filter on.
        where : `dict[str, Any]`, optional
            Additional filters to apply.
        include_deleted : `bool`, default=False
            Whether to include deleted entries.
        limit : `int`, default=100
            Maximum number of results.
        offset : `str`, optional
            Pagination offset.
        fields : `str`, optional
            The fields to return in the response.

        Returns
        -------
        `dict[str, Any]`
            Query result for the filtered program.
        """
        client = self.get_client()
        query = self.get_query(query_id="get_batch_by_program_id", fields=fields)

        program_filter = create_program_id_filter(program_id)

        if where:
            combined_where = {"AND": [program_filter, where]}
        else:
            combined_where = program_filter

        return await _get_batch(
            client=client,
            query=query,
            where=combined_where,
            offset=offset,
            limit=limit,
            include_deleted=include_deleted,
        )
