"""GPP GraphQL Client.

This module provides the GPPClient class for interacting with the GPP GraphQL API.
It manages authentication, transport configuration, and access to namespaced resource
managers for performing queries and mutations.

Examples
--------
>>> client = GPPClient(url="https://gpp.example.org/graphql", auth_token="abc123")
>>> result = await client.program_note.get_by_id(resource_id="n-123")
"""

__all__ = ["GPPClient"]

from typing import Optional, Any

from gql import Client, gql
import aiohttp
from gql.transport.aiohttp import AIOHTTPTransport

from .managers.program_note import ProgramNoteManager


class GPPClient:
    """A client for interacting with the GPP GraphQL API.

    This client manages transport, authentication, and shared resource interfaces.

    Parameters
    ----------
    url : `str`
        The base URL of the GPP GraphQL endpoint.
    auth_token : `str`
        The bearer token used for authorization.

    Attributes
    ----------
    _url : `str`
        The GraphQL endpoint URL.
    _transport : `AIOHTTPTransport`
        The transport layer with configured headers and timeouts.
    _client : `Client`
        The GQL client for executing queries and mutations.
    observation : `ObservationResource`
        Resource manager for observation-related operations.
    """

    def __init__(
        self,
        url: str,
        auth_token: str,
    ) -> None:
        self._url: str = url
        self._transport: AIOHTTPTransport = AIOHTTPTransport(
            url=url,
            headers={"Authorization": f"Bearer {auth_token}"},
            client_session_args={
                "timeout": aiohttp.ClientTimeout(
                    total=300,  # Total timeout in seconds (5 minutes).
                    connect=60,  # Connection timeout.
                    sock_read=60,  # Socket read timeout.
                    sock_connect=60,  # Socket connect timeout.
                )
            },
        )
        try:
            self._client: Client = Client(
                transport=self._transport, fetch_schema_from_transport=True
            )
        except Exception as exc:
            print(exc)

        # TODO: Initialize all resource managers.
        self.program_note = ProgramNoteManager(self)

    async def _execute(
        self,
        query: str,
        variables: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL query or mutation with unified error handling.

        Parameters
        ----------
        query : `str`
            The raw GraphQL query or mutation string.
        variables : `dict[str, Any]`, optional
            A dictionary of variables to pass along with the query.

        Returns
        -------
        `dict[str, Any]`
            The result of the GraphQL execution.

        Raises
        ------
        RuntimeError
            If execution fails for any reason, the underlying exception
            is wrapped and re-raised with context.
        """
        try:
            async with self._client as session:
                return await session.execute(gql(query), variable_values=variables)
        except Exception as exc:
            # TODO: Log error, re-raise custom exception, or retry.
            raise RuntimeError(f"GraphQL execution failed: {exc}") from exc
