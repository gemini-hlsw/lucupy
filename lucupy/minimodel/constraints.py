# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from typing import ClassVar, List, Optional, Sequence, final

import numpy as np
import numpy.typing as npt
from astropy.coordinates import Angle
from astropy.units import Quantity
from astropy import units as u
from scipy.special import erf, erfinv

from lucupy.helpers import flatten
from lucupy.types import ScalarOrNDArray

from ..decorators import immutable
from .timingwindow import TimingWindow

__all__ = [
    'BaseConstraint',
    'CloudCover',
    'Conditions',
    'Constraints',
    'ConstraintUnit',
    'ElevationLimits',
    'ElevationType',
    'ImageQuality',
    'SkyBackground',
    'Strehl',
    'Variant',
    'VariantSnapshot',
    'WaterVapor',
]

@final
class ConstraintUnit(Enum):
    PERCENTILE = 'PERCENTILE'
    ARCSEC = 'ARCSEC'
    MAG = 'MAG'
    MM = 'MM'

@dataclass
class BaseConstraint:
    """
    Continuous real value for a constraint
    """
    # For numpy support, must be higher than NumPy's default priority (which is 0.0)
    __array_priority__ = 1000.0

    def __init__(self, value: float, constraint_unit: ConstraintUnit=ConstraintUnit.PERCENTILE):
        self.value = value
        self.unit = constraint_unit

    def __str__(self):
        if self.unit is ConstraintUnit.PERCENTILE:
            return f"{self.value * 100:.2f}".rstrip("0").rstrip(".")
        else:
            return f"{self.value:.2f}".rstrip("0").rstrip(".")

    def __float__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, np.ndarray):
            return self.value == other
        return self.value == float(other)

    def __le__(self, other):
        if isinstance(other, np.ndarray):
            return self.value <= other
        return self.value <= float(other)

    def __ge__(self, other):
        if isinstance(other, np.ndarray):
            return self.value >= other
        return self.value >= float(other)

    def __lt__(self, other):
        if isinstance(other, np.ndarray):
            return self.value < other
        return self.value < float(other)

    def __gt__(self, other):
        if isinstance(other, np.ndarray):
            return self.value > other
        return self.value > float(other)

    def __ne__(self, other):
        if isinstance(other, np.ndarray):
            return self.value != other
        return self.value != float(other)

    def __add__(self, other):
        if isinstance(other, np.ndarray):
            return self.value + other
        return self.value + float(other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, np.ndarray):
            return self.value - other
        return self.value - float(other)

    def __rsub__(self, other):
        if isinstance(other, np.ndarray):
            return other - self.value
        return float(other) - self.value

    def __mul__(self, other):
        if isinstance(other, np.ndarray):
            return self.value * other
        return self.value * float(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, np.ndarray):
            return self.value / other
        return self.value / float(other)

    def __rtruediv__(self, other):
        if isinstance(other, np.ndarray):
            return other / self.value
        return float(other) / self.value

    @property
    def name(self):
        """
        The name of the bin.
        To keep retro-compatible
        """
        return str(self)

@final
class SkyBackground(BaseConstraint):
    """
    Sky background requirements or current conditions as a continuous property
    """
    def __str__(self):
        if self.unit is ConstraintUnit.PERCENTILE:
            return f"SB{self.value * 100:.2f}".rstrip("0").rstrip(".")
        else:
            return f"SB{self.value:.2f}"

@final
class CloudCover(BaseConstraint):
    """
    Cloud cover requirements or current conditions as a continuous property
    """
    def __str__(self):
        if self.unit is ConstraintUnit.PERCENTILE:
            return f"CC{self.value * 100:.2f}".rstrip("0").rstrip(".")
        else:
            return f"CC{self.value:.2f}"

@final
class ImageQuality(BaseConstraint):
    """
    Continuous value for image quality
    """
    def __str__(self):
        if self.unit is ConstraintUnit.PERCENTILE:
            return f"IQ{self.value * 100:.2f}".rstrip("0").rstrip(".")
        else:
            return f"IQ{self.value:.2f}"

@final
class WaterVapor(BaseConstraint):
    """
    Continuous value for water vapor
    """
    def __str__(self):
        if self.unit is ConstraintUnit.PERCENTILE:
            return f"WV{self.value * 100:.2f}".rstrip("0").rstrip(".")
        else:
            return f"WV{self.value:.2f}"

@final
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


@final
class ElevationType(Enum):
    """
    The type of elevation constraints in the observing conditions.

    Members:
       - NONE
       - HOUR_ANGLE
       - AIRMASS
    """
    NONE = None
    HOUR_ANGLE = "HOUR_ANGLE"
    AIRMASS = "AIRMASS"


@final
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
    def least_restrictive(cls) -> Conditions:
        """
        Return the least possible restrictive conditions.
        """
        return cls(cc=CloudCover(1.0),
                   iq=ImageQuality(1.0),
                   sb=SkyBackground(1.0),
                   wv=WaterVapor(1.0))

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
    def most_restrictive_conditions(conditions: Sequence[Conditions]) -> Conditions:
        """
        Given an iterable of conditions, find the most restrictive amongst the set.
        If no conditions are given, return the most flexible conditions possible.
        """
        if len(conditions) == 0:
            return Conditions.least_restrictive()
        min_cc = min(flatten(c.cc for c in conditions), default=CloudCover(1.0))
        min_iq = min(flatten(c.iq for c in conditions), default=ImageQuality(1.0))
        min_sb = min(flatten(c.sb for c in conditions), default=SkyBackground(1.0))
        min_wv = min(flatten(c.wv for c in conditions), default=WaterVapor(1.0))
        return Conditions(cc=min_cc, iq=min_iq, sb=min_sb, wv=min_wv)


    @staticmethod
    def iq_to_percentile(fwhm: float, wavelength: float, airmass: float, model: str = "web"):
        """
        Calculate the percentile of on-source image quality.
        * `fwhm` in arcsec (on-source)
        * `wavelength` in microns
        * `model` is either `WEB` or `QAP`
        """
        zenith_fwhm = fwhm / airmass ** 0.6

        if model.lower() == 'web':
            # model fit to the IQ constraints listed on the web page
            p = 226.439637 \
                -93.6673981 * wavelength ** -0.162045293 \
                -47.4550797 * zenith_fwhm ** -0.973500276
            pct = max(0, min(100, p))  # ensure in the range 0 - 100

        elif model.lower() == 'qap':
            # model fit to QAP from 2004-2024:  (the extra +0.5 is to force 100% in the worst IQ)
            c = [50.10221383, 0.87712202, 0.78467697, 16.10928544, 0.13778389, -15.8255612, 49.37405633 + 0.5]
            pct = c[0] * erf(c[1] * wavelength**c[2] + c[3] * zenith_fwhm**c[4] + c[5]) + c[6]

        else:
            raise SyntaxError(f'Unknown model: {model}')

        return pct

    @staticmethod
    def percentile_to_iq(pct: float, wavelength: float, airmass: float, model: str):
        """
        Calculate the fwhm for a given IQ percentile, this is the inverse of iq_to_percentile
        * `pct`: percentile
        * `wavelength` in microns
        * `model` is either `WEB` or `QAP`
        """
        # logger = logging.getLogger('percentile_iq')

        if model.lower() == "web":
            # model fit to the IQ constraints listed on the web page
            # p = -93.6673981 * wavelength**-0.162045293 - 47.4550797 * zenith_fwhm**-0.973500276 + 226.439637
            zenith_fwhm = (
                (pct + 93.6673981 * wavelength**-0.162045293 - 226.439637) / -47.4550797
            ) ** (1 / -0.973500276)
        elif model.lower() == "qap":
            # model fit to QAP from 2004-2024:  (the extra +0.5 is to force 100% in the worst IQ)
            c = [
                50.10221383,
                0.87712202,
                0.78467697,
                16.10928544,
                0.13778389,
                -15.8255612,
                49.37405633 + 0.5,
            ]
            # pct = c[0] * erf(c[1] * wavelength**c[2] + c[3] * zenith_fwhm**c[4] + c[5]) + c[6]
            zenith_fwhm = (
                (erfinv((pct - c[6]) / c[0]) - c[1] * wavelength ** c[2] - c[5]) / c[3]
            ) ** (1.0 / c[4])

        else:
            raise SyntaxError(f"Unknown model: {model}")

        fwhm = zenith_fwhm * airmass**0.6

        # logger.debug('IQ: %.2f%%', pct)
        return fwhm

    def __len__(self):
        """
        For array values, return the length of the arrays.
        For scalar values, return a length of 1.
        """
        return len(self.cc) if isinstance(self.cc, np.ndarray) else 1


@final
@immutable
@dataclass(frozen=True)
class ElevationLimits:
    """Equivalent hour angle and airmass limits of the elevation constraints of an observation.

    The elevation_type tells which pair of limits was given: the other pair is derived from it using the
    declination of the target and the latitude of the site (see lucupy.sky.elevation_limits).
    If the declination is not known when the limits are created (e.g. nonsidereal targets), the derived
    pair is None and can be calculated per night with lucupy.sky.complete_elevation_limits.
    If elevation_type is NONE, the given pair are the default airmass limits of the Constraints.

    Attributes:
        elevation_type (ElevationType): Type of the elevation constraints that were given.
        ha_min (float, optional): Minimum hour angle in hours.
        ha_max (float, optional): Maximum hour angle in hours.
        airmass_min (float, optional): Minimum airmass.
        airmass_max (float, optional): Maximum airmass.

        AIRMASS_LIMIT (ClassVar[float]): Largest airmass_max derived from hour angle limits.
    """
    elevation_type: ElevationType
    ha_min: Optional[float]
    ha_max: Optional[float]
    airmass_min: Optional[float]
    airmass_max: Optional[float]

    AIRMASS_LIMIT: ClassVar[float] = field(init=False, default=2.3, repr=False, compare=False)

    @property
    def is_complete(self) -> bool:
        """True if both the hour angle and the airmass limits are known."""
        return None not in (self.ha_min, self.ha_max, self.airmass_min, self.airmass_max)


@final
@immutable
@dataclass(frozen=True)
class Constraints:
    """The constraints required for an observation to be performed.

    Default airmass values to use for elevation constraints if:
        1. The Constraints are not present in the Observation at all; or
        2. The elevation_type is set to NONE.

    Attributes:
        conditions (Conditions): Collection of conditions.
        elevation (ElevationLimits): Hour angle and airmass limits of the elevation constraints.
        timing_windows (List[TimingWindow]): Time windows in the constraints are in effect.
        strehl (Strehl:optional): None

        DEFAULT_AIRMASS_ELEVATION_MIN (ClassVar[float]): 1.0
        DEFAULT_AIRMASS_ELEVATION_MAX (ClassVar[float]): 2.3

    """
    conditions: Conditions
    elevation: ElevationLimits
    timing_windows: List[TimingWindow]
    # clearance_windows: Optional[List[ClearanceWindow]] = None
    strehl: Optional[Strehl] = None

    # Default airmass values to use for elevation constraints if:
    # 1. The Constraints are not present in the Observation at all; or
    # 2. The elevation_type is set to NONE.
    DEFAULT_AIRMASS_ELEVATION_MIN: ClassVar[float] = field(init=False, default=1.0, repr=False, compare=False)
    DEFAULT_AIRMASS_ELEVATION_MAX: ClassVar[float] = field(init=False, default=2.05, repr=False, compare=False)


@final
@immutable
@dataclass(frozen=True)
class Variant:
    """
    A weather variant.
    Attributes:
        iq (Union[npt.NDArray[ImageQuality], ImageQuality]): Image quality.
        cc (Union[npt.NDArray[CloudCover], CloudCover]): Cloud Cover.
        wv (Union[npt.NDArray[WaterVapor], WaterVapor]): Water vapor.
        wind_dir (Angle): Wind direction (degrees).
        wind_spd (Quantity): Wind speed (m/s).
    """
    iq: npt.NDArray[ImageQuality] | ImageQuality
    cc: npt.NDArray[CloudCover] | CloudCover
    wv: npt.NDArray[WaterVapor] | WaterVapor
    wind_dir: Angle
    wind_spd: Quantity

    def __post_init__(self):
        """
        Ensure that if any arrays are specified, all values are specified arrays of the same size.
        """
        is_uniform = len({np.isscalar(self.cc), np.isscalar(self.iq), np.isscalar(self.wv)}) == 1
        if not is_uniform:
            raise ValueError(f'Variant has a mixture of array and scalar types: {self}')

        are_arrays = isinstance(self.cc, np.ndarray)
        array_lengths = {np.asarray(self.wind_dir).size,
                         np.asarray(self.wind_spd).size}
        if are_arrays:
            uniform_lengths = len({len(self.cc), len(self.iq), len(self.wv)}.union(array_lengths)) == 1
        else:
            uniform_lengths = len(array_lengths) == 1
        if not uniform_lengths:
            raise ValueError(f'Variant has a variable number of array sizes: {self}')


@final
@immutable
@dataclass(frozen=True)
class VariantSnapshot:
    """
    A snapshot of a variant: this is used to keep track of weather changes or the current state of
    the weather at a site.

    wind_dir should be in degrees.
    wind_speed should be in m / s.

    Attributes:
        iq (ImageQuality): Image quality.
        cc (CloudCover): Cloud cover.
        wv (WaterVapor): Water vapor.
        wind_dir (Angle): Wind direction (in degrees). Should be scalar.
        wind_spd (Quantity): Wind speed (in m/s). Should be scalar.
    """
    iq: ImageQuality
    cc: CloudCover
    wv: WaterVapor
    wind_dir: Angle
    wind_spd: Quantity

    def __post_init__(self):
        if self.wind_dir.size != 1:
            raise ValueError(f'Wind direction should be scalar, but has size {self.wind_dir.size}.')
        if self.wind_spd.unit != u.m / u.s:
            raise ValueError(f'Wind speed should be in m / s, but {self.wind_spd.unit} specified.')
        if self.wind_spd.size != 1:
            raise ValueError(f'Wind speed should be scalar, but has size {self.wind_spd.size}.')

    def make_variant(self, num_timeslots: int) -> Variant:
        """
        Create a Variant object with the specified number of timeslots.
        """
        if num_timeslots <= 0:
            raise ValueError(f'Request to make a Variant for illegal number of timeslots: {num_timeslots}.')

        cc_array = np.array([self.cc] * num_timeslots)
        iq_array = np.array([self.iq] * num_timeslots)
        wv_array = np.array([self.wv] * num_timeslots)
        wind_dir_array = Angle(np.full(num_timeslots, self.wind_dir.value), unit=self.wind_dir.unit)
        wind_spd_array = np.full(num_timeslots, self.wind_spd.value) * self.wind_spd.unit
        return Variant(iq=iq_array,
                       cc=cc_array,
                       wv=wv_array,
                       wind_dir=wind_dir_array,
                       wind_spd=wind_spd_array)
