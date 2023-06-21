# Copyright (c) 2016-2023 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import pytest
import numpy as np

from lucupy.minimodel import CloudCover
from lucupy.helpers import lerp, lerp_enum, lerp_radians


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
                          (np.pi/2 + 1e3, 3*np.pi/2, 4, np.array([2.97794378, 3.41155508, 3.84516638, 4.27877768])),
                          (np.pi/2 + 1e3, -np.pi/2, 4, np.array([2.97794378, 3.41155508, 3.84516638, 4.27877768])),
                          (np.pi/4, -np.pi/4, 3, np.array([0.39269908, 0, 5.89048623])),
                          (-np.pi/4, np.pi/4, 3, np.array([5.89048623, 0, 0.39269908]))])
def test_lerp_radians(first_value, last_value, n, expected):
    assert np.allclose(lerp_radians(first_value, last_value, n), expected)
