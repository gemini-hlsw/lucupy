# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from lucupy.resourcemanager import ResourceManager
from lucupy.minimodel.resource import ResourceType


__all__ = [
    'STANDARD_INSTRUMENTS',
    'NIR_INSTRUMENTS',
    'OTHER_INSTRUMENTS',
    'INSTRUMENTS',
]

# Obtain Resource from them by going through the ResourceManager.
rm = ResourceManager()

standard_instruments_names = frozenset({
    'Flamingos2',
    'GNIRS',
    'NIFS',
    'IGRINS',
})

STANDARD_INSTRUMENTS = frozenset(rm.lookup_resource(resource_id=inst_name, resource_type=ResourceType.INSTRUMENT)
                                 for inst_name in standard_instruments_names)


# Names of the NIR instruments that do not fall under STANDARD_INSTRUMENTS.
nir_instrument_names = frozenset({
    'NIRI',
    'Phoenix',
})

NIR_INSTRUMENTS = frozenset(rm.lookup_resource(resource_id=inst_name, resource_type=ResourceType.INSTRUMENT)
                            for inst_name in nir_instrument_names) | STANDARD_INSTRUMENTS

other_instrument_names = frozenset({
    'GMOS-N',
    'GMOS-S',
    'GPI',
    'GSAOI',
})

OTHER_INSTRUMENTS = frozenset(rm.lookup_resource(resource_id=inst_name, resource_type=ResourceType.INSTRUMENT)
                              for inst_name in other_instrument_names)


INSTRUMENTS = NIR_INSTRUMENTS | OTHER_INSTRUMENTS


