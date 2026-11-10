# Copyright (c) 2016-2026 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from lucupy.minimodel import ResourceType
from lucupy.resource_manager import ResourceManager

# Unlikely to clash with anything another test put in the singleton's cache.
_BARCODE = '10999999'


def test_a_later_description_fills_in_a_missing_one():
    rm = ResourceManager()
    # As the availability files load it: a bare barcode.
    bare = rm.lookup_resource(_BARCODE, rtype=ResourceType.FPU)
    assert bare.description is None

    # As an observation's MDF lookup does.
    named = rm.lookup_resource(_BARCODE, description='GN2026BQ999-01')

    assert named.description == 'GN2026BQ999-01'
    assert named.type == ResourceType.FPU
    # Still the same resource wherever the bare one is held.
    assert named == bare and hash(named) == hash(bare)
    assert named in frozenset({bare})
    assert rm.lookup_resource(_BARCODE).description == 'GN2026BQ999-01'


def test_a_type_is_filled_in_with_the_description():
    rm = ResourceManager()
    rm.lookup_resource(_BARCODE + '2')

    assert rm.lookup_resource(_BARCODE + '2', 'name', ResourceType.FPU).type == ResourceType.FPU


def test_an_existing_description_is_kept():
    rm = ResourceManager()
    rm.lookup_resource(_BARCODE + '1', description='first', rtype=ResourceType.FPU)

    assert rm.lookup_resource(_BARCODE + '1', description='second').description == 'first'
