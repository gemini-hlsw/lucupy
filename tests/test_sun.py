# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import astropy.units as u
import numpy.testing as nptest
import pytest
from astropy.time import Time

from lucupy.sky.sun import Sun

from .fixtures import location, midnight, test_time


@pytest.mark.usefixtures("midnight")
def test_sun_location_at_midnight(midnight):
    """
    Test that the sun location is at the equator at J2000.
    """
    pos = Sun.at(midnight)
    assert pos.ra.value == pytest.approx(100.88591931021546)
    assert pos.dec.value == pytest.approx(23.058699652854724)


@pytest.mark.usefixtures("test_time", "location")
def test_sun_time_by_altitude(test_time, location):
    """
    Test that the sun location is at the equator at J2000.
    """
    alt = 0.0 * u.deg
    expected = Time("2020-07-01 05:01:07.885")
    sun_time_by_altitude = Sun.time_by_altitude(alt, test_time - (5.0 * u.hr), location)
    nptest.assert_almost_equal(sun_time_by_altitude.jd, expected.jd, decimal=3)
