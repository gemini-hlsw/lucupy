# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import astropy.units as u
import numpy.testing as nptest
import pytest
from astropy.time import Time

from lucupy.sky.moon import Moon

from .fixtures import location, test_time


@pytest.fixture
def moon():
    return Moon().at(Time("2020-07-01 9:25:00", format='iso', scale='utc'))


@pytest.mark.usefixtures("location")
def test_moon_accurate_location(moon, location):
    """
    Test that the moon location is accurate.
    """
    loc, dist = moon.accurate_location(location)
    nptest.assert_almost_equal(loc.ra.deg, 228.468331589897, decimal=3)
    nptest.assert_almost_equal(loc.dec.deg, -15.238277160913936, decimal=3)
    nptest.assert_almost_equal(dist.value, 365466974.5885662, decimal=3)


@pytest.mark.usefixtures("location")
def test_moon_low_precision_location(moon, location):
    """
    Test that the moon location is accurate.
    """
    loc, dist = moon.low_precision_location(location)
    nptest.assert_almost_equal(loc.ra.deg, 228.41771177093597, decimal=5)
    nptest.assert_almost_equal(loc.dec.deg, -15.297127679461509, decimal=5)
    nptest.assert_almost_equal(dist.value, 57.34667914568056, decimal=5)


@pytest.mark.usefixtures("test_time", "location")
def test_moon_time_by_altitude(moon, test_time, location):
    """
    Test that the moon location is accurate.
    """
    alt = 0.0 * u.deg
    expected = Time('2020-07-01 12:38:21.732')
    moon_time_by_altitude = moon.time_by_altitude(alt, test_time, location)
    nptest.assert_almost_equal(expected.jd, moon_time_by_altitude.jd, decimal=2)
