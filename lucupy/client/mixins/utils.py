__all__ = ["create_program_id_filter"]

from typing import Any


def create_program_id_filter(program_id: str) -> dict[str, Any]:
    """Return a GraphQL filter for matching a specific program ID."""
    return {"program": {"id": {"EQ": program_id}}}
