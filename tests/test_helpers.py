# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from datetime import timedelta

import astropy.units as u
import numpy as np
import pytest
from astropy.time import TimeDelta

from lucupy.helpers import (is_contiguous, lerp, lerp_degrees, lerp_enum,
                            lerp_radians, time_delta_astropy_to_minutes,
                            timedelta_astropy_to_python)
from lucupy.minimodel import CloudCover


@pytest.mark.parametrize('first_value, last_value, n, expected',
                         [(0, 11, 10, np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])),
                          (0, 0, 10, np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))])
def test_lerp(first_value, last_value, n, expected):
    assert np.allclose(lerp(first_value, last_value, n), expected)


@pytest.mark.parametrize('first_value, last_value, n, expected',
                         [(0.5, 1.0, 5, np.array([0.7, 0.7, 0.8, 1.0, 1.0])),
                          (0.5, 1.0, 6, np.array([0.7, 0.7, 0.8, 0.8, 1.0, 1.0])),
                          (1.0, 0.5, 5, np.array([1.0, 1.0, 0.8, 0.7, 0.7])),
                          (1.0, 0.5, 6, np.array([1.0, 1.0, 0.8, 0.8, 0.7, 0.7])),
                          (0.5, 1.0, 1, np.array([0.8])),
                          (1.0, 0.5, 1, np.array([0.8])),
                          (0.7, 0.7, 3, np.array([0.7, 0.7, 0.7]))])
def test_lerp_enum(first_value, last_value, n, expected):
    assert np.allclose(lerp_enum(CloudCover, first_value, last_value, n), expected)


@pytest.mark.parametrize('first_value, last_value, n, expected',
                         [(np.pi/2, 3*np.pi/2, 4, np.array([0.9424778, 0.31415927, 5.96902604, 5.34070751])),
                          (np.pi/2, -np.pi/2, 4, np.array([0.9424778, 0.31415927, 5.96902604, 5.34070751])),
                          (np.pi/2 + 1e-3, 3*np.pi/2, 4, np.array([2.19991486, 2.82803339, 3.45615192, 4.08427045])),
                          (np.pi/2 + 1e-3, -np.pi/2, 4, np.array([2.19991486, 2.82803339, 3.45615192, 4.08427045])),
                          (np.pi/4, -np.pi/4, 3, np.array([0.39269908, 0, 5.89048623])),
                          (-np.pi/4, np.pi/4, 3, np.array([5.89048623, 0, 0.39269908]))])
def test_lerp_radians(first_value, last_value, n, expected):
    assert np.allclose(lerp_radians(first_value, last_value, n), expected)


@pytest.mark.parametrize('first_value, last_value, n, expected',
                         [(90, 270, 4, np.array([54, 18, 342, 306])),
                          (90, -90, 4, np.array([54, 18, 342, 306])),
                          (270, 90, 4, np.array([234, 198, 162, 126])),
                          (-90, 90, 4, np.array([234, 198, 162, 126])),
                          (90 + 1e-8, 270, 4, np.array([126, 162, 198, 234])),
                          (90 + 1e-8, -90, 4, np.array([126, 162, 198, 234])),
                          (60, 300, 3, np.array([30, 0, 330])),
                          (60, -60, 3, np.array([30, 0, 330]))])
def test_lerp_degrees(first_value, last_value, n, expected):
    assert np.allclose(lerp_degrees(first_value, last_value, n), expected)


@pytest.mark.parametrize('time_delta',
                         [TimeDelta([1.0, 2.0] * u.minute),
                          TimeDelta([] * u.minute)])
def test_time_delta_astropy_to_python_exception(time_delta):
    with pytest.raises(ValueError):
        timedelta_astropy_to_python(time_delta)


@pytest.mark.parametrize('time_delta, expected',
                         [(TimeDelta(1.0 * u.minute), timedelta(seconds=60)),
                          (TimeDelta(1.5 * u.minute), timedelta(seconds=90))])
def test_time_delta_astropy_to_python(time_delta, expected):
    assert timedelta_astropy_to_python(time_delta) == expected


@pytest.mark.parametrize('time_delta',
                         [TimeDelta([1.0, 2.0] * u.minute),
                          TimeDelta(1.5 * u.minute)])
def test_time_delta_astropy_to_minutes_exceptions(time_delta):
    with pytest.raises(ValueError):
        time_delta_astropy_to_minutes(time_delta)


@pytest.mark.parametrize('time_delta, expected',
                         [(TimeDelta(1.0 * u.minute), 1),
                          (TimeDelta(2.0 * u.minute), 2)])
def test_time_delta_astropy_to_minutes(time_delta, expected):
    assert time_delta_astropy_to_minutes(time_delta) == expected


@pytest.mark.parametrize('iterable, expected',
                         [((1, 3, 2), True),
                          ([1, 5, 3, 2, 4], True),
                          ({1, 4, 2, 3}, True),
                          ({1: 'a', 2: 'b', 4: 'c', 3: 'd'}, True),
                          (np.array([1]), True),
                          (np.array([5, 3, 2, 1, 4]), True),
                          (np.array([5, 4, 1]), False)])
def test_is_contiguous(iterable, expected):
    assert is_contiguous(iterable) == expected
