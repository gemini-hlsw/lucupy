"""
This module provides reusable mixins for updating resources via GraphQL,
supporting batch updates, updates by ID, and updates filtered by program ID.
"""

__all__ = ["UpdateByIdViaBatchMixin", "UpdateBatchMixin", "UpdateBatchByProgramIdMixin"]

from typing import Any, Optional

from .utils import create_program_id_filter


# TODO: Write a _update_by_id.


async def _update_batch(
    *,
    client: Any,
    query: str,
    set_values: dict[str, Any],
    where: Optional[dict[str, Any]] = None,
    limit: int = 100,
    include_deleted: bool = False,
) -> dict[str, Any]:
    """Execute a GraphQL update mutation on a batch of resources.

    Parameters
    ----------
    client : `Any`
        The GraphQL client instance.
    query : `str`
        The mutation query string with a `{fields}` placeholder.
    set_values : `dict[str, Any]`
        The fields to update in each matched resource.
    where : `dict[str, Any]`, optional
        The filter criteria for selecting resources.
    limit : `int`, default=100
        The maximum number of resources to update.
    include_deleted : `bool`, default=False
        Whether to include deleted resources in the update.

    Returns
    -------
    `dict[str, Any]`
        The result of the mutation, including updated resources.
    """
    input_data = {
        "SET": set_values,
        "WHERE": where,
        "LIMIT": limit,
        "includeDeleted": include_deleted,
    }
    return await client._execute(query=query, variables={"input": input_data})


class UpdateByIdViaBatchMixin:
    """Provides an update_by_id method using a batch-style update query."""

    async def update_by_id(
        self,
        *,
        resource_id: str,
        set_values: dict[str, Any],
        include_deleted: bool = False,
        fields: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update a single resource by its ID.

        Parameters
        ----------
        resource_id : `str`
            The ID of the resource to update.
        set_values : `dict[str, Any]`
            Fields to update on the resource.
        include_deleted : `bool`, default=False
            Whether to include deleted resources in the update.
        fields : `str`, optional
            Fields to return in the response. Uses default if not provided.

        Returns
        -------
        `dict[str, Any]`
            The updated resource.
        """
        client = self.get_client()
        query = self.get_query(query_id="update_by_id", fields=fields)

        where = {"id": {"EQ": resource_id}}

        return await _update_batch(
            client=client,
            query=query,
            set_values=set_values,
            where=where,
            limit=1,
            include_deleted=include_deleted,
        )


class UpdateBatchMixin:
    """Provides update_batch for updating multiple resources using a where clause."""

    async def update_batch(
        self,
        *,
        set_values: dict[str, Any],
        where: dict[str, Any],
        limit: int = 100,
        include_deleted: bool = False,
        fields: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update multiple resources matching a given filter.

        Parameters
        ----------
        set_values : `dict[str, Any]`
            Fields to update in each matching resource.
        where : `dict[str, Any]`
            The filter for selecting resources to update.
        limit : `int`, default=100
            Maximum number of resources to update.
        include_deleted : `bool`, default=False
            Whether to include deleted resources in the update.
        fields : `str`, optional
            Fields to return in the response. Uses default if not provided.

        Returns
        -------
        `dict[str, Any]`
            The updated resources and `hasMore` flag.
        """
        client = self.get_client()
        query = self.get_query(query_id="update_batch", fields=fields)

        return await _update_batch(
            client=client,
            query=query,
            set_values=set_values,
            where=where,
            limit=limit,
            include_deleted=include_deleted,
        )


class UpdateBatchByProgramIdMixin:
    """Provides update_batch_by_program_id for filtering updates by program."""

    async def update_batch_by_program_id(
        self,
        *,
        program_id: str,
        set_values: dict[str, Any],
        where: Optional[dict[str, Any]] = None,
        limit: int = 100,
        include_deleted: bool = False,
        fields: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update resources matching a program ID and optional filters.

        Parameters
        ----------
        program_id : `str`
            The program ID to match.
        set_values : `dict[str, Any]`
            Fields to update in matching resources.
        where : `dict[str, Any]`, optional
            Additional filter conditions.
        limit : `int`, default=100
            Maximum number of resources to update.
        include_deleted : `bool`, default=False
            Whether to include deleted resources in the update.
        fields : `str`, optional
            Fields to return in the response. Uses default if not provided.

        Returns
        -------
        `dict[str, Any]`
            The updated resources and `hasMore` flag.
        """
        client = self.get_client()
        query = self.get_query(query_id="update_batch_by_program_id", fields=fields)

        program_filter = create_program_id_filter(program_id)

        if where:
            combined_where = {"AND": [program_filter, where]}
        else:
            combined_where = program_filter

        return await _update_batch(
            client=client,
            query=query,
            set_values=set_values,
            where=combined_where,
            limit=limit,
            include_deleted=include_deleted,
        )
