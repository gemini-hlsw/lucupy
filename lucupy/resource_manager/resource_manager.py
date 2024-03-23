# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from typing import Dict, Optional, final

from lucupy.meta import Singleton

from lucupy.minimodel.resource import Resource
from lucupy.minimodel.resource_type import ResourceType

_all__ = [
    'ResourceManager',
]


@final
class ResourceManager(metaclass=Singleton):
    """
    A singleton class that manages Resource instances to reuse them as per the flyweight design pattern.
    """
    def __init__(self):
        """
        Create an empty dictionary of mappings from name to Resource.
        """
        self._all_resources: Dict[str, Resource] = {}

    def lookup_resource(self,
                        rid: str,
                        description: Optional[str] = None,
                        rtype: Optional[ResourceType] = ResourceType.NONE) -> Optional[Resource]:
        """
        Function to perform Resource caching and minimize the number of Resource objects by attempting to reuse
        Resource objects with the same ID.

        If resource_id evaluates to False, return None.
        Otherwise, check if a Resource with id already exists.
        If it does, return it.
        If not, create it, add it to the map of all Resources, and then return it.

        Note that even if multiple objects do exist with the same ID, they will be considered equal by the
        Resource equality comparator.
        """
        # The Resource constructor raises an exception for id None or containing any capitalization of "none".
        if not rid:
            return None
        if rid not in self._all_resources:
            self._all_resources[rid] = Resource(id=rid, description=description,
                                                type=rtype, legal_creation=True)
        return self._all_resources[rid]
