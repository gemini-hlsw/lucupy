# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from dataclasses import replace
from typing import Optional, Tuple

import astropy.units as u
import numpy as np
from astropy.coordinates import Angle

from lucupy.minimodel import Constraints, ElevationLimits, ElevationType

from .altitude import Altitude, AngleParam
from .utils import airmass_to_alt, alt_to_hour_angle, true_airmass

__all__ = [
    'airmass_to_hour_angle_limits',
    'hour_angle_to_airmass_limits',
    'elevation_limits',
    'complete_elevation_limits',
]


def airmass_to_hour_angle_limits(airmass_max: float,
                                 dec: AngleParam,
                                 lat: AngleParam) -> Tuple[float, float]:
    """Hour angle limits equivalent to a maximum airmass.

    The limits are symmetrical around the meridian.
    If the target is always below airmass_max, the limits are (-12, 12).
    If it never reaches airmass_max, the limits are (0, 0).

    Args:
        airmass_max: Maximum airmass.
        dec: Declination of the target.
        lat: Latitude of the site.

    Returns:
        The (ha_min, ha_max) tuple in hours.
    """
    alt_airmass_max = airmass_to_alt(airmass_max)
    ha = alt_to_hour_angle(dec, lat, alt_airmass_max)

    # alt_to_hour_angle returns -1000 rad if the target is always above the altitude
    # and +1000 rad if it is always below (its docstring has them the other way around).
    if ha.value == -1000.0:
        ha_hours = 12.0
    elif ha.value == 1000.0:
        ha_hours = 0.0
    else:
        ha_hours = abs(float(ha.to_value(u.hourangle)))
    return -ha_hours, ha_hours


def hour_angle_to_airmass_limits(ha_min: float,
                                 ha_max: float,
                                 dec: AngleParam,
                                 lat: AngleParam) -> Tuple[float, float]:
    """Airmass limits equivalent to hour angle limits.

    airmass_max is the largest airmass at either hour angle limit, capped at ElevationLimits.AIRMASS_LIMIT.
    airmass_min is 1.0 if the hour angle limits include the meridian, else the smallest airmass at
    either hour angle limit.

    Args:
        ha_min: Minimum hour angle in hours.
        ha_max: Maximum hour angle in hours.
        dec: Declination of the target.
        lat: Latitude of the site.

    Returns:
        The (airmass_min, airmass_max) tuple.
    """
    alt, _, _ = Altitude.above(dec, Angle([ha_min, ha_max], unit=u.hourangle), lat)
    airmass = true_airmass(alt)

    airmass_max = min(float(np.max(airmass)), ElevationLimits.AIRMASS_LIMIT)
    airmass_min = 1.0 if ha_min < 0.0 < ha_max else float(np.min(airmass))
    return airmass_min, airmass_max


def elevation_limits(elevation_type: ElevationType,
                     elevation_min: Optional[float],
                     elevation_max: Optional[float],
                     dec: Optional[AngleParam],
                     lat: AngleParam) -> ElevationLimits:
    """Create the ElevationLimits for the elevation constraints of an observation.

    Airmass constraints are converted to hour angles using only the maximum airmass, as a minimum airmass
    above 1.0 would split the visible hour angles in two ranges.
    If the elevation type is NONE, the default airmass limits of the Constraints are used.
    If dec is None, the derived limits are left as None.

    Args:
        elevation_type: Type of the elevation constraints.
        elevation_min: Minimum hour angle in hours or minimum airmass. Ignored if the type is NONE.
        elevation_max: Maximum hour angle in hours or maximum airmass. Ignored if the type is NONE.
        dec: Declination of the target, if known.
        lat: Latitude of the site.

    Returns:
        The ElevationLimits.
    """
    if elevation_type == ElevationType.HOUR_ANGLE:
        limits = ElevationLimits(elevation_type=elevation_type,
                                 ha_min=float(elevation_min),
                                 ha_max=float(elevation_max),
                                 airmass_min=None,
                                 airmass_max=None)
    elif elevation_type == ElevationType.AIRMASS:
        limits = ElevationLimits(elevation_type=elevation_type,
                                 ha_min=None,
                                 ha_max=None,
                                 airmass_min=float(elevation_min),
                                 airmass_max=float(elevation_max))
    else:
        limits = ElevationLimits(elevation_type=ElevationType.NONE,
                                 ha_min=None,
                                 ha_max=None,
                                 airmass_min=Constraints.DEFAULT_AIRMASS_ELEVATION_MIN,
                                 airmass_max=Constraints.DEFAULT_AIRMASS_ELEVATION_MAX)

    return limits if dec is None else complete_elevation_limits(limits, dec, lat)


def complete_elevation_limits(limits: ElevationLimits,
                              dec: AngleParam,
                              lat: AngleParam) -> ElevationLimits:
    """Calculate the missing hour angle or airmass limits.

    Limits that are already known are kept, so this can be called per night with the declination of
    that night for nonsidereal targets.

    Args:
        limits: ElevationLimits, possibly with the derived limits as None.
        dec: Declination of the target.
        lat: Latitude of the site.

    Returns:
        The ElevationLimits with both the hour angle and the airmass limits.
    """
    if limits.is_complete:
        return limits

    if limits.elevation_type == ElevationType.HOUR_ANGLE:
        airmass_min, airmass_max = hour_angle_to_airmass_limits(limits.ha_min, limits.ha_max, dec, lat)
        return replace(limits, airmass_min=airmass_min, airmass_max=airmass_max)

    ha_min, ha_max = airmass_to_hour_angle_limits(limits.airmass_max, dec, lat)
    return replace(limits, ha_min=ha_min, ha_max=ha_max)
