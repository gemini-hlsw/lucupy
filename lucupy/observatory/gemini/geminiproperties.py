# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from __future__ import annotations

from enum import Enum, EnumMeta
from typing import final

import astropy.units as u
from astropy.time import Time

from lucupy.minimodel.observationmode import ObservationMode, ObservationModes
from lucupy.minimodel.resource import Resource, Resources
from lucupy.minimodel.resource_type import ResourceType
from lucupy.minimodel.wavelength import Wavelengths
from lucupy.resource_manager.resource_manager import ResourceManager
from lucupy.observatory.abstract import ObservatoryProperties

__all__ = ['GeminiProperties']

rm = ResourceManager()


@final
class GeminiProperties(ObservatoryProperties):
    """
    Implementation of ObservatoryCalculations specific to Gemini.
    """

    class _InstrumentsMeta(EnumMeta):
        """Metaclass for the Instruments Class below.
        """
        def __contains__(cls, r: Resource) -> bool:  # type: ignore[override]
            return any(inst.value.id in r.id for inst in cls.__members__.values())  # type: ignore[var-annotated]

    class Instruments(Enum, metaclass=_InstrumentsMeta):
        """ Gemini-specific instruments.
        """
        FLAMINGOS2 = rm.lookup_resource(rid='Flamingos2', rtype=ResourceType.INSTRUMENT)
        NIFS = rm.lookup_resource(rid='NIFS', rtype=ResourceType.INSTRUMENT)
        NIRI = rm.lookup_resource(rid='NIRI', rtype=ResourceType.INSTRUMENT)
        IGRINS = rm.lookup_resource(rid='IGRINS', rtype=ResourceType.INSTRUMENT)
        GMOS_N = rm.lookup_resource(rid='GMOS-N', rtype=ResourceType.INSTRUMENT)
        GMOS_S = rm.lookup_resource(rid='GMOS-S', rtype=ResourceType.INSTRUMENT)
        GNIRS = rm.lookup_resource(rid='GNIRS', rtype=ResourceType.INSTRUMENT)
        GPI = rm.lookup_resource(rid='GPI', rtype=ResourceType.INSTRUMENT)
        GSAOI = rm.lookup_resource(rid='GSAOI', rtype=ResourceType.INSTRUMENT)
        PHOENIX = rm.lookup_resource(rid='Phoenix', rtype=ResourceType.INSTRUMENT)

    _STANDARD_INSTRUMENTS = frozenset({Instruments.FLAMINGOS2,
                                       Instruments.GNIRS,
                                       Instruments.NIFS,
                                       Instruments.IGRINS})

    _NIR_INSTRUMENTS: Resources = frozenset({Instruments.FLAMINGOS2,
                                             Instruments.GNIRS,
                                             Instruments.NIRI,
                                             Instruments.NIFS,
                                             Instruments.PHOENIX,
                                             Instruments.IGRINS})

    """ List: Instruments for which there are set standards.
    """
    @staticmethod
    def determine_standard_time(resources: Resources,
                                wavelengths: Wavelengths,
                                modes: ObservationModes,
                                cal_length: int) -> Time:
        """Determine the standard star time required for Gemini.

        Args:
            resources (Resources): Instruments to be used.
            wavelengths (Wavelength): Wavelengths to be observed.
            modes (ObservationModes): Observation modes.
            cal_length (int): The specific length of a calibration.

        Returns:
            Time: _description_

        Todo:
            We may only want to include specific resources, in which case, modify
            Instruments above to be StandardInstruments.

        """
        if cal_length > 1:
            # Check to see if any of the resources are instruments.
            if any(resource in GeminiProperties._STANDARD_INSTRUMENTS for resource in resources):
                if all(wavelength <= 2.5 for wavelength in wavelengths):
                    return 1.5 * u.h
                else:
                    return 1.0 * u.h
            if ObservationMode.IMAGING in modes:
                return 2.0 * u.h
            return 0.0 * u.h

    @staticmethod
    def instruments() -> Resources:
        return GeminiProperties._STANDARD_INSTRUMENTS | GeminiProperties._NIR_INSTRUMENTS

    @staticmethod
    def nir_instruments() -> Resources:
        return GeminiProperties._NIR_INSTRUMENTS

    @staticmethod
    def is_nir_instrument(resource: Resource) -> bool:
        """
        Checks in the specified Resource is a NIR Gemini Instrument.
        """
        return resource in GeminiProperties._NIR_INSTRUMENTS

    @staticmethod
    def is_instrument(resource: Resource) -> bool:
        """Checks if the resource is a Gemini instrument.

        Args:
            resource (Resource): A resource to be checked.

        Returns:
            bool: True if resource is a Gemini instrument.
        """
        return resource in GeminiProperties._STANDARD_INSTRUMENTS | GeminiProperties._NIR_INSTRUMENTS
