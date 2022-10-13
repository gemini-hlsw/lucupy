# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

# This has to be outside of Observation to avoid circular imports.
from enum import Enum


class ObservationMode(str, Enum):
    """Observation Mode

    Members:
        - UNKNOWN = 'unknown'
        - IMAGING = 'imaging'
        - LONGSLIT = 'longslit'
        - IFU = 'ifu'
        - MOS = 'mos'
        - XD = 'xd'
        - CORON = 'coron'
        - NRM = 'nrm'
    """
    # TODO: This is not stored anywhere and is only used temporarily in the atom code in the
    # TODO: OcsProgramExtractor. Should it be stored anywhere or is it only used in intermediate
    # TODO: calculations? It seems to depend on the instrument and FPU.

    UNKNOWN = 'unknown'
    IMAGING = 'imaging'
    LONGSLIT = 'longslit'
    IFU = 'ifu'
    MOS = 'mos'
    XD = 'xd'
    CORON = 'coron'
    NRM = 'nrm'
