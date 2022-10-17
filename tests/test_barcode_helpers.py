# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import pytest

from lucupy.helpers import barcode_to_mask, mask_to_barcode


@pytest.mark.parametrize('mask, inst, expected', [('GS2017BLP005-34', 'GMOS', '11200534'),
                                                  ('0.75arcsec', None, '10005373')])
def test_mask_to_barcode(mask, inst, expected):
    assert mask_to_barcode(mask, inst) == expected


@pytest.mark.parametrize('barcode, rootname, expected', [('10005381', 'GS2017', 'PinholeC'),
                                                         ('11310101', 'GS2017', 'GS2017BFT101-01'), ])
def test_barcode_to_mask(barcode, rootname, expected):
    assert barcode_to_mask(barcode, rootname) == expected
