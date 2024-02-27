# All code in this package is a refactored, numpy-vectorized version of thorskyutil.py:
#
# https://github.com/jrthorstensen/thorsky/blob/master/thorskyutil.py
#
# utility and miscellaneous time and the sky routines built mostly on astropy.
#
# Copyright John Thorstensen, 2018, who graciously has allowed Gemini to use this code under the BSD-3 Clause license.
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

"""
Constants that are used here and there.  Some are Quantities,
others are just floats. Not all are used.

The planet-coefs are for series expansions for the phase functions
of the planets, used in predicting apparent magnitude. See code.
"""

from math import pi
from typing import Final

import astropy.units as u
from astropy.coordinates.distances import Distance
from astropy.time import Time

__all__ = [
    'PI',
    'TWOPI',
    'PI_OVER_2',
    'ARCSEC_IN_RADIAN',
    'DEG_IN_RADIAN',
    'HRS_IN_RADIAN',
    'KMS_AUDAY',
    'SPEED_OF_LIGHT',
    'SS_MASS',
    'J2000',
    'J2000_Time',
    'JYEAR',
    'JYEAR_100',
    'SEC_IN_DAY',
    'FLATTEN',
    'EQUAT_RAD',
    'EARTHRAD_IN_AU',
    'ASTRO_UNIT',
    'RSUN',
    'RMOON',
    'PLANET_TOL',
    'KZEN',
]

PI: Final[float] = pi
TWOPI: Final[float] = 2 * PI
PI_OVER_2: Final[float] = PI / 2
ARCSEC_IN_RADIAN: Final[float] = 360 * 60 * 60 / (2 * PI)
DEG_IN_RADIAN: Final[float] = 180 / PI
HRS_IN_RADIAN: Final[float] = 24 / (2 * PI)
KMS_AUDAY: Final[float] = 1731.45683633  # km per sec in 1 AU/day
SPEED_OF_LIGHT: Final[float] = 299792.458  # in km per sec ... exact.
SS_MASS: Final[float] = 1.00134198  # solar system mass in solar units
J2000: Final[float] = 2451545.  # Julian date at standard epoch
J2000_Time: Final[Time] = Time(2451545., format='jd')  # J2000 rendered as a Time
JYEAR: Final[float] = 365.25 # noqa
JYEAR_100: Final[float] = JYEAR * 100 # noqa
SEC_IN_DAY: Final[float] = 86400.
FLATTEN: Final[float] = 0.003352813  # flattening of earth, 1/298.257
EQUAT_RAD: Final[Distance] = 6378137. * u.m  # equatorial radius of earth, meters
EARTHRAD_IN_AU: Final[float] = 23454.7910556298  # number of earth rad in 1 au
ASTRO_UNIT: Final[float] = 1.4959787066e11  # 1 AU in meters
RSUN: Final[float] = 6.96000e8  # IAU 1976 recom. solar radius, meters
RMOON: Final[float] = 1.738e6  # IAU 1976 recom. lunar radius, meters
PLANET_TOL: Final[float] = 3.  # flag if nearer than 3 degrees
KZEN: Final[float] = 0.172  # mag / airmass relation for Hale Pohaku
