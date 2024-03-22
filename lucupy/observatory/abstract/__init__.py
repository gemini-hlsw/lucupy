# Copyright (c) 2016-2023 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from __future__ import annotations

from abc import ABC
from datetime import timedelta
from typing import Optional, cast

from astropy.time import Time

from lucupy.minimodel.observationmode import ObservationMode, ObservationModes
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
    def is_instrument(resource: Resource) -> bool:
        """Determine if the given resource is an instrument or not.

        Args:
            resource (Resource): An instrument.

        Returns:
            bool: True is the resource is an instrument of the Observatory, otherwise False.
        """
        return ObservatoryProperties._check().is_instrument(resource)
