# Copyright (c) 2016-2023 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

"""
A small version of GPP data model
"""
from typing import NewType

from .atom import *
from .constraints import *
from .group import *
from .ids import *
from .magnitude import *
from .observation import *
from .observationmode import *
from .program import *
from .qastate import *
from .resource import *
from .semester import *
from .site import *
from .target import *
from .timeallocation import *
from .timingwindow import *
from .too import *
from .wavelength import *

# Type alias for a night index and night indices.
NightIndex = NewType('NightIndex', int)
NightIndices = npt.NDArray[NightIndex]

# Type alias for a time slot index and time slot indices.
TimeslotIndex = NewType('TimeslotIndex', int)
TimeslotIndices = npt.NDArray[TimeslotIndex]
