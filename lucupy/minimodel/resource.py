# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from dataclasses import dataclass, field, InitVar
from typing import FrozenSet, Optional, TypeAlias, final

from .resource_type import ResourceType
from lucupy.decorators import immutable

__all__ = [
    'Resource',
    'Resources',
]


@final
@immutable
@dataclass(frozen=True)
class Resource:
    """This is a general observatory resource.
    It can consist of

    * a guider;
    * an instrument;
    * a part of an instrument;
    * an observatory (Site); or even
    * personnel

    and is used to determine what observations can be
    performed at a given time based on the resource availability.

    ***NOTE:***
    Instances of Resource should NEVER be created directly through this dataclass.
    Resources are flyweight objects, and should ONLY be created through ResourceManager.lookup_resource.

    Attributes:
        id (str): Resource id or name.
        description (str): Short description.
    """
    id: str
    description: Optional[str] = None
    type: Optional[ResourceType] = ResourceType.NONE
    legal_creation: InitVar[bool] = field(default=False)

    def __post_init__(self, legal_creation: bool) -> None:
        if not legal_creation:
            raise RuntimeError(f'Resource object {self.id} attempted to be created directly. '
                               'All resources must be accessed through ResourceManager.lookup_resource.')
        if self.id is None or 'NONE' in self.id.upper():
            raise ValueError('Should not have any Resources equal to None or containing "None"')

    def __hash__(self):
        """
        We only want to hash the ID. Resources with identical IDs should be considered identical.
        """
        return hash(self.id)

    def __eq__(self, other):
        """
        Resources are the same if the have the same ID.
        """
        return isinstance(other, Resource) and self.id == other.id

    def __repr__(self):
        return f"Resource(id='{self.id}')"


Resources: TypeAlias = FrozenSet[Resource]
