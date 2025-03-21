"""Restore mixins for soft-deleted GraphQL resources.

This module provides reusable mixins to restore resources by ID or in batch
based on a program ID, using a batch-style update mutation to set `existence`
to "PRESENT".
"""

__all__ = ["RestoreByIdViaBatchMixin", "RestoreBatchByProgramIdMixin"]

from typing import Any, Optional

from .utils import create_program_id_filter
from .update import _update_batch


async def _restore_batch(
    *,
    client: Any,
    query: str,
    where: dict[str, Any],
    limit: int = 100,
    include_deleted: bool = True,
) -> dict[str, Any]:
    """Internal helper to restore resources by setting existence to PRESENT.

    Parameters
    ----------
    client : `Any`
        The GraphQL client instance.
    query : `str`
        The update mutation query string.
    where : `dict[str, Any]`
        Filter to select which resources to restore.
    limit : `int`, default=100
        Maximum number of resources to restore.
    include_deleted : `bool`, default=True
        Whether to include already-deleted resources in the match.

    Returns
    -------
    `dict[str, Any]`
        Result of the restore mutation.
    """
    return await _update_batch(
        client=client,
        query=query,
        set_values={"existence": "PRESENT"},
        where=where,
        limit=limit,
        include_deleted=include_deleted,
    )


class RestoreByIdViaBatchMixin:
    """Restore a single resource by ID using batch mutation."""

    async def restore_by_id(
        self,
        *,
        resource_id: str,
        include_deleted: bool = True,
        fields: Optional[str] = None,
    ) -> dict[str, Any]:
        """Restore a single resource by its ID.

        Parameters
        ----------
        resource_id : `str`
            The unique ID of the resource to restore.
        include_deleted : `bool`, default=True
            Whether to include already-deleted records.
        fields : `str`, optional
            The fields to return in the response.

        Returns
        -------
        `dict[str, Any]`
            The restored resource result.
        """
        client = self.get_client()
        query = self.get_query(query_id="restore_by_id", fields=fields)

        return await _restore_batch(
            client=client,
            query=query,
            where={"id": {"EQ": resource_id}},
            limit=1,
            include_deleted=include_deleted,
        )


class RestoreBatchByProgramIdMixin:
    """Restore a batch of resources associated with a specific program ID."""

    async def restore_batch_by_program_id(
        self,
        *,
        program_id: str,
        where: Optional[dict[str, Any]] = None,
        limit: int = 100,
        include_deleted: bool = True,
        fields: Optional[str] = None,
    ) -> dict[str, Any]:
        """Restore multiple resources linked to a program.

        Parameters
        ----------
        program_id : `str`
            The program ID to match.
        where : `dict[str, Any]`, optional
            Additional filters to apply alongside the program ID.
        limit : `int`, default=100
            Maximum number of resources to restore.
        include_deleted : `bool`, default=True
            Whether to include already-deleted resources.
        fields : `str`, optional
            The fields to return in the response.

        Returns
        -------
        `dict[str, Any]`
            The restored resources and metadata.
        """
        client = self.get_client()
        query = self.get_query(query_id="restore_batch_by_program_id", fields=fields)

        program_filter = create_program_id_filter(program_id)

        if where:
            combined_where = {"AND": [program_filter, where]}
        else:
            combined_where = program_filter

        return await _restore_batch(
            client=client,
            query=query,
            where=combined_where,
            limit=limit,
            include_deleted=include_deleted,
        )
