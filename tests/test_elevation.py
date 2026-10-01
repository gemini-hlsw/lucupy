# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import astropy.units as u
import pytest
from astropy.coordinates import Angle

from lucupy.minimodel import Constraints, ElevationLimits, ElevationType
from lucupy.sky.altitude import Altitude
from lucupy.sky.elevation import (airmass_to_hour_angle_limits, complete_elevation_limits, elevation_limits,
                                  hour_angle_to_airmass_limits)
from lucupy.sky.utils import true_airmass

# Gemini South
LAT = Angle(-30.24075, unit=u.deg)
DEC = Angle(-60.0, unit=u.deg)


def _airmass(ha_hours: float, dec: Angle = DEC) -> float:
    alt, _, _ = Altitude.above(dec, Angle(ha_hours, unit=u.hourangle), LAT)
    return float(true_airmass(alt))


def test_airmass_to_hour_angle_limits_are_symmetrical():
    ha_min, ha_max = airmass_to_hour_angle_limits(1.5, DEC, LAT)
    assert ha_min == pytest.approx(-ha_max)
    assert _airmass(ha_max) == pytest.approx(1.5, abs=5e-3)


def test_airmass_to_hour_angle_limits_always_below_airmass():
    assert airmass_to_hour_angle_limits(2.3, Angle(-89.0, unit=u.deg), LAT) == (-12.0, 12.0)


def test_airmass_to_hour_angle_limits_never_reaches_airmass():
    ha_min, ha_max = airmass_to_hour_angle_limits(2.0, Angle(60.0, unit=u.deg), LAT)
    assert (ha_min, ha_max) == pytest.approx((0.0, 0.0))


def test_hour_angle_to_airmass_limits_across_meridian():
    airmass_min, airmass_max = hour_angle_to_airmass_limits(-1.0, 2.0, DEC, LAT)
    assert airmass_min == 1.0
    assert airmass_max == pytest.approx(_airmass(2.0))


@pytest.mark.parametrize('ha_min, ha_max, closest', [(1.0, 3.0, 1.0), (-3.0, -1.0, -1.0)])
def test_hour_angle_to_airmass_limits_one_side_of_meridian(ha_min, ha_max, closest):
    airmass_min, airmass_max = hour_angle_to_airmass_limits(ha_min, ha_max, DEC, LAT)
    assert airmass_min == pytest.approx(_airmass(closest))
    assert airmass_max == pytest.approx(_airmass(3.0))


def test_hour_angle_to_airmass_limits_capped():
    _, airmass_max = hour_angle_to_airmass_limits(-6.0, 6.0, Angle(0.0, unit=u.deg), LAT)
    assert airmass_max == ElevationLimits.AIRMASS_LIMIT


def test_elevation_limits_hour_angle():
    limits = elevation_limits(ElevationType.HOUR_ANGLE, -2.0, 4.0, DEC, LAT)
    assert limits.elevation_type == ElevationType.HOUR_ANGLE
    assert (limits.ha_min, limits.ha_max) == (-2.0, 4.0)
    assert limits.airmass_min == 1.0
    assert limits.airmass_max == pytest.approx(_airmass(4.0))


def test_elevation_limits_airmass():
    limits = elevation_limits(ElevationType.AIRMASS, 1.0, 1.5, DEC, LAT)
    assert (limits.airmass_min, limits.airmass_max) == (1.0, 1.5)
    assert _airmass(limits.ha_max) == pytest.approx(1.5, abs=5e-3)


def test_elevation_limits_none_uses_default_airmass():
    limits = elevation_limits(ElevationType.NONE, None, None, DEC, LAT)
    assert limits.elevation_type == ElevationType.NONE
    assert limits.airmass_min == Constraints.DEFAULT_AIRMASS_ELEVATION_MIN
    assert limits.airmass_max == Constraints.DEFAULT_AIRMASS_ELEVATION_MAX
    assert limits.is_complete


def test_elevation_limits_without_dec_leaves_derived_limits_empty():
    limits = elevation_limits(ElevationType.AIRMASS, 1.0, 1.5, None, LAT)
    assert (limits.ha_min, limits.ha_max) == (None, None)
    assert not limits.is_complete


def test_complete_elevation_limits_fills_missing_limits():
    limits = elevation_limits(ElevationType.AIRMASS, 1.0, 1.5, None, LAT)
    assert complete_elevation_limits(limits, DEC, LAT) == elevation_limits(ElevationType.AIRMASS, 1.0, 1.5, DEC, LAT)


def test_complete_elevation_limits_keeps_complete_limits():
    limits = elevation_limits(ElevationType.HOUR_ANGLE, -2.0, 4.0, DEC, LAT)
    assert complete_elevation_limits(limits, Angle(0.0, unit=u.deg), LAT) is limits
