# Copyright (c) 2016-2023 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import pytest
import numpy as np

from lucupy.minimodel import CloudCover
from lucupy.helpers import lerp_enum


@pytest.mark.parametrize('first_value, last_value, n, expected',
                         [(0.5, 1.0, 5, np.array([0.5, 0.5, 0.7, 0.8, 0.8])),
                          (0.5, 1.0, 6, np.array([0.5, 0.5, 0.7, 0.7, 0.8, 0.8])),
                          (1.0, 0.5, 5, np.array([0.8, 0.8, 0.7, 0.5, 0.5])),
                          (1.0, 0.5, 6, np.array([0.8, 0.8, 0.7, 0.7, 0.5, 0.5])),
                          (0.5, 1.0, 1, np.array([0.7])),
                          (1.0, 0.5, 1, np.array([0.7]))])
def test_lerp_enum(first_value, last_value, n, expected):
    assert np.array_equal(lerp_enum(CloudCover, first_value, last_value, n), expected)
