# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from dataclasses import dataclass
from enum import IntEnum, auto
from typing import FrozenSet, Optional, TypeAlias, final

from lucupy.decorators import immutable

__all__ = [
    'NIR_INSTRUMENTS',
    'Resource',
    'Resources',
    'ResourceType',
]


# TODO: Not sure why this is an IntEnum and not just an Enum.
@final
class ResourceType(IntEnum):
    """A Resource's type

    Members:
        - SITE
        - WFS
        - INSTRUMENT
        - FPU
        - DISPERSER
    """
    NONE = auto()
    SITE = auto()
    WFS = auto()
    INSTRUMENT = auto()
    FPU = auto()
    DISPERSER = auto()


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

    Attributes:
        id (str): Resource id or name.
        description (str): Short description.
    """
    id: str
    description: Optional[str] = None
    type: Optional[ResourceType] = ResourceType.NONE

    def __post_init__(self):
        if self.id is None or 'NONE' in self.id.upper():
            raise ValueError('Should not have any Resources equal to None or containing "None"')

    def __eq__(self, other):
        return isinstance(other, Resource) and self.id == other.id

    def __repr__(self):
        return f"Resource(id='{self.id}')"


Resources: TypeAlias = FrozenSet[Resource]

NIR_INSTRUMENTS: Resources = frozenset([Resource('Flamingos2', type=ResourceType.INSTRUMENT),
                                        Resource('GNIRS', type=ResourceType.INSTRUMENT),
                                        Resource('NIRI', type=ResourceType.INSTRUMENT),
                                        Resource('NIFS', type=ResourceType.INSTRUMENT),
                                        Resource('Phoenix', type=ResourceType.INSTRUMENT),
                                        Resource('IGRINS', type=ResourceType.INSTRUMENT)])
