# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from datetime import timedelta
from enum import Enum, EnumMeta
from typing import FrozenSet, Optional

import astropy.units as u
from astropy.time import Time

from lucupy.minimodel import ObservationMode, Resource, Site
from lucupy.observatory.abstract import ObservatoryProperties


class GeminiProperties(ObservatoryProperties):
    """
    Implementation of ObservatoryCalculations specific to Gemini.
    """

    class _InstrumentsMeta(EnumMeta):
        def __contains__(cls, r: Resource) -> bool:
            return any(inst.value.id in r.id for inst in cls.__members__.values())

    # Gemini-specific instruments.
    class Instruments(Enum, metaclass=_InstrumentsMeta):
        FLAMINGOS2 = Resource('Flamingos2')
        NIFS = Resource('NIFS')
        NIRI = Resource('NIRI')
        IGRINS = Resource('IGRINS')
        GMOS_S = Resource('GMOS-S')
        GMOS_N = Resource('GMOS-N')
        GNIRS = Resource('GNIRS')
        GPI = Resource('GPI')
        GSAOI = Resource('GSAOI')

    # Instruments for which there are set standards.
    _STANDARD_INSTRUMENTS = [Instruments.FLAMINGOS2,
                             Instruments.GNIRS,
                             Instruments.NIFS,
                             Instruments.IGRINS]

    @staticmethod
    def determine_standard_time(resources: FrozenSet[Resource],
                                wavelengths: FrozenSet[float],
                                modes: FrozenSet[ObservationMode],
                                cal_length: int) -> Time:
        """
        Determine the standard star time required for Gemini.
        """
        if cal_length > 1:
            # Check to see if any of the resources are instruments.
            # TODO: We may only want to include specific resources, in which case, modify
            # TODO: Instruments above to be StandardInstruments.
            if any(resource in GeminiProperties._STANDARD_INSTRUMENTS for resource in resources):
                if all(wavelength <= 2.5 for wavelength in wavelengths):
                    return 1.5 * u.h
                else:
                    return 1.0 * u.h
            if ObservationMode.IMAGING in modes:
                return 2.0 * u.h
            return 0.0 * u.h

    @staticmethod
    def is_instrument(resource: Resource) -> bool:
        return resource in GeminiProperties.Instruments

    @staticmethod
    def acquisition_time(resource: Resource, observation_mode: ObservationMode) -> Optional[timedelta]:
        if not GeminiProperties.is_instrument(resource):
            return None
        ...
