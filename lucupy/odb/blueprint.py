from dataclasses import dataclass, fields
from typing import FrozenSet, Iterator, Any

from lucupy.minimodel import Site, ALL_SITES

__all__ = [
    'QueryBlueprint',
]


@dataclass
class QueryBlueprint:
    """
    Set of parameters the client uses to query the database.

    Attributes:
        obs_with_sequence (bool): Allows observation to use the sequence fragments. Defaults to False.
        site (FrozenSet[Site]): Allow filtering by site in case of Groups or Observations that are used
            only in one site. If only one site is used and the Group contains information from both the resulting
            object would be incomplete. Defaults to ALL_SITES (Both GS and GN)
    """
    obs_with_sequence: bool = False
    site: FrozenSet[Site] = ALL_SITES

    def __iter__(self) -> Iterator[Any]:
        return iter(getattr(self, field.name) for field in fields(self))