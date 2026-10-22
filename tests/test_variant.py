# Copyright (c) 2016-2026 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import astropy.units as u
import numpy as np
import pytest
from astropy.coordinates import Angle

from lucupy.minimodel import CloudCover, ImageQuality, Variant, VariantSnapshot, WaterVapor


def _snapshot() -> VariantSnapshot:
    return VariantSnapshot(iq=ImageQuality(0.7),
                           cc=CloudCover(0.5),
                           wv=WaterVapor(0.8),
                           wind_dir=Angle(90, unit=u.deg),
                           wind_spd=5 * (u.m / u.s))


def test_make_variant_includes_water_vapor():
    variant = _snapshot().make_variant(4)
    assert len(variant.wv) == 4
    assert all(wv == 0.8 for wv in variant.wv)


def test_variant_rejects_water_vapor_of_different_length():
    variant = _snapshot().make_variant(3)
    with pytest.raises(ValueError):
        Variant(iq=variant.iq, cc=variant.cc, wv=np.array([WaterVapor(0.8)] * 2),
                wind_dir=variant.wind_dir, wind_spd=variant.wind_spd)
