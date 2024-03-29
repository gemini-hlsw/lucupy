# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import astropy.units as u
import numpy.testing as nptest
import pytest
from astropy.coordinates import Angle, Longitude

from lucupy.sky.altitude import Altitude

from .fixtures import coord, location


@pytest.mark.usefixtures('coord', 'location')
def test_altitude_above_zero(coord, location):
    """
    Test that altitude is 0 at the equator.
    """
    alt, az, parallac = Altitude.above(coord[0].dec, -3.0 * u.hourangle, location.lat)

    expected_alt = Angle(0.84002209, unit=u.rad)
    expected_az = Longitude(1.1339171, unit=u.radian)
    expected_par = Angle(-1.6527975, unit=u.radian)

    nptest.assert_almost_equal(alt.rad, expected_alt.rad, decimal=3)
    nptest.assert_almost_equal(az.rad, expected_az.rad, decimal=3)
    nptest.assert_almost_equal(parallac.rad, expected_par.rad, decimal=3)
