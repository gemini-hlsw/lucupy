# Copyright (c) 2016-2023 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from __future__ import annotations

from abc import ABC
from typing import Optional, cast

from astropy.time import Time

from lucupy.minimodel.observationmode import ObservationModes
from lucupy.minimodel.resource import Resource, Resources
from lucupy.minimodel.wavelength import Wavelengths

__all__ = [
    'ObservatoryProperties',
]


class ObservatoryProperties(ABC):
    """Observatory-specific methods.

       These are not tied to other components or
       structures, and allow computations to be implemented in one place.

    """
    _properties: Optional[ObservatoryProperties] = None

    @staticmethod
    def set_properties(cls) -> None:
        """Set properties for an specific Observatory

        Raises:
            ValueError: Illegal properties value.

        """
        if not issubclass(cls, ObservatoryProperties):
            raise ValueError('Illegal properties value.')
        ObservatoryProperties._properties = cls()

    @staticmethod
    def _check() -> ObservatoryProperties:
        """ Check if the properties have been set.

        Raises:
            ValueError: Properties have not been set.
        """
        if ObservatoryProperties._properties is None:
            raise ValueError('Observatory properties have not been set.')
        return cast(ObservatoryProperties, ObservatoryProperties._properties)

    @staticmethod
    def determine_standard_time(resources: Resources,
                                wavelengths: Wavelengths,
                                modes: ObservationModes,
                                cal_length: int) -> Time:
        """Determine standard time for a specific Observatory

        Args:
            resources (Resources): Set of Resources(instruments, mask, etc).
            wavelengths (Wavelengths): An array of Wavelengths to be observed.
            modes (ObservationModes): The different modes of observation.
            cal_length (int): The length (in seconds) of a calibration.

        Returns:
            Time: Value(s) of standard time
        """
        return ObservatoryProperties._check().determine_standard_time(
            resources,
            wavelengths,
            modes,
            cal_length
        )

    @staticmethod
    def nir_instruments() -> Resources:
        return ObservatoryProperties._check().nir_instruments()

    @staticmethod
    def instruments() -> Resources:
        return ObservatoryProperties._check().instruments()

    @staticmethod
    def is_nir_instrument(resource: Resource) -> bool:
        return ObservatoryProperties._check().is_nir_instrument(resource)

    @staticmethod
    def is_instrument(resource: Resource) -> bool:
        """Determine if the given resource is an instrument or not.

        Args:
            resource (Resource): An instrument.

        Returns:
            bool: True is the resource is an instrument of the Observatory, otherwise False.
        """
        return ObservatoryProperties._check().is_instrument(resource)
