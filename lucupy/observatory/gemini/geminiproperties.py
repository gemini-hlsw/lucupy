# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from datetime import timedelta
from enum import Enum, EnumMeta
from typing import FrozenSet, Optional

import astropy.units as u
from astropy.time import Time

from lucupy.minimodel import ObservationMode, Resource
from lucupy.observatory.abstract import ObservatoryProperties


class GeminiProperties(ObservatoryProperties):
    """Implementation of ObservatoryCalculations specific to Gemini.
    """

    class _InstrumentsMeta(EnumMeta):
        """Meta class for the Instruments Class below.
        """
        def __contains__(cls, r: Resource) -> bool:
            return any(inst.value.id in r.id for inst in cls.__members__.values())

    class Instruments(Enum, metaclass=_InstrumentsMeta):
        """ Gemini-specific instruments.
        """
        FLAMINGOS2 = Resource('Flamingos2')
        NIFS = Resource('NIFS')
        NIRI = Resource('NIRI')
        IGRINS = Resource('IGRINS')
        GMOS_S = Resource('GMOS-S')
        GMOS_N = Resource('GMOS-N')
        GNIRS = Resource('GNIRS')
        GPI = Resource('GPI')
        GSAOI = Resource('GSAOI')

    _STANDARD_INSTRUMENTS = [Instruments.FLAMINGOS2,
                             Instruments.GNIRS,
                             Instruments.NIFS,
                             Instruments.IGRINS]
    """ List: Instruments for which there are set standards.
    """

    @staticmethod
    def determine_standard_time(resources: FrozenSet[Resource],
                                wavelengths: FrozenSet[float],
                                modes: FrozenSet[ObservationMode],
                                cal_length: int) -> Time:
        """Determine the standard star time required for Gemini.

        Args:
            resources (FrozenSet[Resource]): Instruments to be used.
            wavelengths (FrozenSet[float]): Wavelengths to be observed.
            modes (FrozenSet[ObservationMode]): Observation modes.
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
    def is_instrument(resource: Resource) -> bool:
        """Checks if the resource is a Gemini instrument.

        Args:
            resource (Resource): A resource to be checked.

        Returns:
            bool: True if resource is a Gemini instrument.
        """
        return resource in GeminiProperties.Instruments

    @staticmethod
    def acquisition_time(resource, observation_mode) -> Optional[timedelta]:
        """_summary_

        Args:
            resource (Resource): Instruments used.
            observation_mode (ObservationMode): Observation mode.

        Returns:
            Optional[timedelta]: _description_
        """
        if not GeminiProperties.is_instrument(resource):
            return None
        ...
