# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from typing import NewType, TypeAlias

import numpy.typing as npt

from .atom import *
from .constraints import *
from .group import *
from .ids import *
from .magnitude import *
from .obs_filter import *
from .observation import *
from .observationmode import *
from .program import *
from .qastate import *
from .resource import *
from .resource_type import *
from .semester import *
from .site import *
from .target import *
from .timeallocation import *
from .timingwindow import *
from .too import *
from .wavelength import *

# Type alias for a night index and night indices.
NightIndex = NewType('NightIndex', int)
NightIndices: TypeAlias = npt.NDArray[NightIndex]

# Type alias for a time slot index and time slot indices.
TimeslotIndex = NewType('TimeslotIndex', int)
TimeslotIndices: TypeAlias = npt.NDArray[TimeslotIndex]
