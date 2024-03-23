# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from enum import auto, Enum
from typing import final

__all__ = ['ResourceType']


@final
class ResourceType(Enum):
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
