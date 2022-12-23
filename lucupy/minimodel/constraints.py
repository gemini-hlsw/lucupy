# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum, auto
from typing import ClassVar, List, Optional, Sequence, Union

import numpy as np
import numpy.typing as npt
from astropy.coordinates import Angle
from astropy.units import Quantity

from lucupy.helpers import flatten
from lucupy.types import ScalarOrNDArray

from .timingwindow import TimingWindow
from ..decorators import immutable


class SkyBackground(float, Enum):
    """
    Bins for observation sky background requirements or current conditions.

    Members:
        - SB20 = 0.2
        - SB50 = 0.5
        - SB80 = 0.8
        - SBANY = 1.0

    """
    SB20 = 0.2
    SB50 = 0.5
    SB80 = 0.8
    SBANY = 1.0


class CloudCover(float, Enum):
    """
    Bins for observation cloud cover requirements or current conditions.

    Members:
        - CC50 = 0.5
        - CC70 = 0.7
        - CC80 = 0.8
        - CCANY = 1.0
    """
    CC50 = 0.5
    CC70 = 0.7
    CC80 = 0.8
    CCANY = 1.0


class ImageQuality(float, Enum):
    """
    Bins for observation image quality requirements or current conditions.

    Members:
        - IQ20 = 0.2
        - IQ70 = 0.7
        - IQ85 = 0.85
        - IQANY = 1.0

    """
    IQ20 = 0.2
    IQ70 = 0.7
    IQ85 = 0.85
    IQANY = 1.0


class WaterVapor(float, Enum):
    """
    Bins for observation water vapor requirements or current conditions.

    Members:
        - WV20 = 0.2
        - WV50 = 0.5
        - WV80 = 0.8
        - WVANY = 1.0

    """
    WV20 = 0.2
    WV50 = 0.5
    WV80 = 0.8
    WVANY = 1.0


class Strehl(float, Enum):
    """
    The Strehl ratio is a measure of the quality of optical image formation.
    Used variously in situations where optical resolution is compromised due to lens aberrations or due to imaging
    through the turbulent atmosphere, the Strehl ratio has a value between 0 and 1, with a hypothetical, perfectly
    unaberrated optical system having a Strehl ratio of 1. (Source: Wikipedia.)

    Members:
        - S00 = 0.0
        - S02 = 0.2
        - S04 = 0.4
        - S06 = 0.6
        - S08 = 0.8
        - S10 = 1.0

    """
    S00 = 0.0
    S02 = 0.2
    S04 = 0.4
    S06 = 0.6
    S08 = 0.8
    S10 = 1.0


class ElevationType(IntEnum):
    """
    The type of elevation constraints in the observing conditions.

    Members:
       - NONE
       - HOUR_ANGLE
       - AIRMASS
    """
    NONE = auto()
    HOUR_ANGLE = auto()
    AIRMASS = auto()


@immutable
@dataclass(frozen=True)
class Conditions:
    """
    A set of conditions.

    Note that we make this dataclass eq and ordered so that we can compare one
    set of conditions with another to see if one satisfies the other.

    This should be done via:
    current_conditions <= required_conditions.

    Attributes:
        cc (ScalarOrNDArray[CloudCover]): CloudCover
        iq (ScalarOrNDArray[ImageQuality]): ImageQuality
        sb (ScalarOrNDArray[SkyBackground]): SkyBackground
        wv (ScalarOrNDArray[WaterVapor]): WaterVapor

    """
    cc: ScalarOrNDArray[CloudCover]
    iq: ScalarOrNDArray[ImageQuality]
    sb: ScalarOrNDArray[SkyBackground]
    wv: ScalarOrNDArray[WaterVapor]

    # Least restrictive conditions.
    @classmethod
    def least_restrictive(cls) -> 'Conditions':
        """
        Return the least possible restrictive conditions.
        """
        return cls(cc=CloudCover.CCANY,
                   iq=ImageQuality.IQANY,
                   sb=SkyBackground.SBANY,
                   wv=WaterVapor.WVANY)

    def __post_init__(self):
        """
        Ensure that if any arrays are specified, all values are specified arrays of the same size.
        """
        is_uniform = len({np.isscalar(self.cc), np.isscalar(self.iq), np.isscalar(self.sb), np.isscalar(self.wv)}) == 1
        if not is_uniform:
            raise ValueError(f'Conditions have a mixture of array and scalar types: {self}')

        are_arrays = isinstance(self.cc, np.ndarray)
        if are_arrays:
            uniform_lengths = len({self.cc.size, self.iq.size, self.sb.size, self.wv.size}) == 1
            if not uniform_lengths:
                raise ValueError(f'Conditions have a variable number of array sizes: {self}')

    @staticmethod
    def most_restrictive_conditions(conditions: Sequence['Conditions']) -> 'Conditions':
        """
        Given an iterable of conditions, find the most restrictive amongst the set.
        If no conditions are given, return the most flexible conditions possible.
        """
        if len(conditions) == 0:
            return Conditions.least_restrictive()
        min_cc = min(flatten(c.cc for c in conditions), default=CloudCover.CCANY)
        min_iq = min(flatten(c.iq for c in conditions), default=ImageQuality.IQANY)
        min_sb = min(flatten(c.sb for c in conditions), default=SkyBackground.SBANY)
        min_wv = min(flatten(c.wv for c in conditions), default=WaterVapor.WVANY)
        return Conditions(cc=min_cc, iq=min_iq, sb=min_sb, wv=min_wv)

    def __len__(self):
        """
        For array values, return the length of the arrays.
        For scalar values, return a length of 1.
        """
        return len(self.cc) if isinstance(self.cc, np.ndarray) else 1


@immutable
@dataclass(frozen=True)
class Constraints:
    """The constraints required for an observation to be performed.

    Default airmass values to use for elevation constraints if:
        1. The Constraints are not present in the Observation at all; or
        2. The elevation_type is set to NONE.

    Attributes:
        conditions (Conditions): Collection of conditions.
        elevation_type (ElevationType): Elevation type.
        elevation_min (float): Max value of elevation.
        elevation_max (float): Min value of elevation.
        timing_windows (List[TimingWindow]): Time windows in the constraints are in effect.
        strehl (Strehl:optional): None

        DEFAULT_AIRMASS_ELEVATION_MIN (ClassVar[float]): 1.0
        DEFAULT_AIRMASS_ELEVATION_MAX (ClassVar[float]): 2.3

    """
    conditions: Conditions
    # constrast: Constrast
    elevation_type: ElevationType
    elevation_min: float
    elevation_max: float
    timing_windows: List[TimingWindow]
    # clearance_windows: Optional[List[ClearanceWindow]] = None
    strehl: Optional[Strehl] = None

    # Default airmass values to use for elevation constraints if:
    # 1. The Constraints are not present in the Observation at all; or
    # 2. The elevation_type is set to NONE.
    DEFAULT_AIRMASS_ELEVATION_MIN: ClassVar[float] = field(init=False, default=1.0, repr=False, compare=False)
    DEFAULT_AIRMASS_ELEVATION_MAX: ClassVar[float] = field(init=False, default=2.3, repr=False, compare=False)


@immutable
@dataclass(frozen=True)
class Variant:
    """A weather variant.
    wind_speed should be in m / s.

    Attributes:

        start_time (datetime): Time of the variant.
        iq (Union[npt.NDArray[ImageQuality], ImageQuality]): Image quality.
        cc (Union[npt.NDArray[CloudCover], CloudCover]): Cloud Cover.
        wind_dir (Angle): Wind direction.
        wind_spd (Quantity): Wind speed.

    """
    # TODO: No idea what time blocks are. Note this could be a list or a single value.
    # TODO: Because of this, we cannot hash Variants, which is problematic.

    start_time: datetime
    iq: Union[npt.NDArray[ImageQuality], ImageQuality]
    cc: Union[npt.NDArray[CloudCover], CloudCover]
    wind_dir: Angle
    wind_spd: Quantity

    def __post_init__(self):
        """
        Ensure that if any arrays are specified, all values are specified arrays of the same size.
        """
        is_uniform = len({np.isscalar(self.cc), np.isscalar(self.iq)}) == 1
        if not is_uniform:
            raise ValueError(f'Variant has a mixture of array and scalar types: {self}')

        are_arrays = isinstance(self.cc, np.ndarray)
        array_lengths = {np.asarray(self.wind_dir).size,
                         np.asarray(self.wind_spd).size}
        if are_arrays:
            uniform_lengths = len({len(self.cc), len(self.iq)}.union(array_lengths)) == 1
        else:
            uniform_lengths = len(array_lengths) == 1
        if not uniform_lengths:
            raise ValueError(f'Variant has a variable number of array sizes: {self}')
