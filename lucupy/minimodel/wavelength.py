# Copyright (c) 2016-2023 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from typing import FrozenSet, NewType

Wavelength = NewType('Wavelength', float)
Wavelengths = FrozenSet[float]
