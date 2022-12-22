# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from ..decorators import immutable


class MagnitudeSystem(Enum):
    """
    List of magnitude systems associated with magnitude bands.

    Members:
       - VEGA
       - AB
       - JY
    """
    VEGA = auto()
    AB = auto()
    JY = auto()


@immutable
@dataclass(frozen=True)
class MagnitudeBand:
    """They are fully enumerated in MagnitudeBands, so they should be looked up by name there.
    THIS CLASS SHOULD NOT BE INSTANTIATED.

    Values for center and width are specified in microns.

    Attributes:
        name (str):
        center (float):
        width (float):
        system (MagnitudeSystem): Default to MagnitudeSystem.VEGA .
        description (str, optional): Default to None.

    """
    name: str
    center: float
    width: float
    system: MagnitudeSystem = MagnitudeSystem.VEGA
    description: Optional[str] = None


class MagnitudeBands(Enum):
    """
    It is unconventional to use lowercase characters in an enum, but to differentiate
    them from the uppercase magnitude bands, we must.

    Look up the MagnitudeBand from this Enum as follows:
    MagnitudeBands[name]

    """
    u = MagnitudeBand('u', 0.356, 0.046, MagnitudeSystem.AB, 'UV')
    g = MagnitudeBand('g', 0.483, 0.099, MagnitudeSystem.AB, 'green')
    r = MagnitudeBand('r', 0.626, 0.096, MagnitudeSystem.AB, 'red')
    i = MagnitudeBand('i', 0.767, 0.106, MagnitudeSystem.AB, 'far red')
    z = MagnitudeBand('z', 0.910, 0.125, MagnitudeSystem.AB, 'near-infrared')
    U = MagnitudeBand('U', 0.360, 0.075, description='ultraviolet')
    B = MagnitudeBand('B', 0.440, 0.090, description='blue')
    V = MagnitudeBand('V', 0.550, 0.085, description='visual')
    UC = MagnitudeBand('UC', 0.610, 0.063, description='UCAC')
    R = MagnitudeBand('R', 0.670, 0.100, description='red')
    I = MagnitudeBand('I', 0.870, 0.100, description='infrared')
    Y = MagnitudeBand('Y', 1.020, 0.120)
    J = MagnitudeBand('J', 1.250, 0.240)
    H = MagnitudeBand('H', 1.650, 0.300)
    K = MagnitudeBand('K', 2.200, 0.410)
    L = MagnitudeBand('L', 3.760, 0.700)
    M = MagnitudeBand('M', 4.770, 0.240)
    N = MagnitudeBand('N', 10.470, 5.230)
    Q = MagnitudeBand('Q', 20.130, 1.650)
    AP = MagnitudeBand('AP', 0.550, 0.085, description='apparent')


@immutable
@dataclass(frozen=True)
class Magnitude:
    """A magnitude value in a particular band.

    Attributes:
        band (MagnitudeBands):
        value (float):
        error (float): Default to None.
    """
    band: MagnitudeBands
    value: float
    error: Optional[float] = None
