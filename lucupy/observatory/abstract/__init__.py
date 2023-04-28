# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from abc import ABC
from datetime import timedelta
from typing import FrozenSet, Optional, Union

from astropy.time import Time  # type: ignore


class ObservatoryProperties(ABC):
    """Observatory-specific methods.

       These are not tied to other components or
       structures, and allow computations to be implemented in one place.

    """
    _properties: Optional[Union[None, 'ObservatoryProperties']] = None

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
    def _check_properties() -> None:
        """ Check if any properties are set

        Raises:
            ValueError: Properties have not been set.

        """
        if ObservatoryProperties._properties is None:
            raise ValueError('Properties have not been set.')

    @staticmethod
    def determine_standard_time(resources: FrozenSet,
                                wavelengths: FrozenSet[float],
                                modes: FrozenSet,
                                cal_length: int) -> Time:
        """Determine standard time for a specific Observatory

        Args:
            resources (FrozenSet): Set of Resources(instruments, mask, etc).
            wavelengths (FrozenSet[float]): An array of Wavelengths to be observed.
            modes (FrozenSet): The different modes of observation.
            cal_length (int): The length (in seconds) of a calibration.

        Returns:
            Time: Value(s) of standard time
        """
        if ObservatoryProperties._properties is not None:
            ObservatoryProperties._check_properties()
            return ObservatoryProperties._properties.determine_standard_time(
                resources,
                wavelengths,
                modes,
                cal_length
            )
        else:
            raise ValueError('Properties have not been set.')

    @staticmethod
    def is_instrument(resource) -> bool:  # type: ignore
        """Determine if the given resource is an instrument or not.

        Args:
            resource (Resource): An instrument.

        Returns:
            bool: True is the resource is an instrument of the Observatory, otherwise False.
        """
        if ObservatoryProperties._properties is not None:
            return ObservatoryProperties._properties.is_instrument(resource)
        else:
            raise ValueError('Properties have not been set.')

    @staticmethod
    def acquisition_time(resource, observation_mode) -> Optional[timedelta]:  # type: ignore
        """Given a resource, check if it is an instrument, and if so, lookup the
           acquisition time for the specified mode.

        Args:
            resource (Resource): A resource that should be an Instrument.
            observation_mode (ObservationMode): The observation mode to be used.

        Returns:
            Optional[timedelta]: The acquisition time for the instrument in that specific mode.
        """
        if ObservatoryProperties._properties is not None:
            return ObservatoryProperties._properties.acquisition_time(resource, observation_mode)
        else:
            raise ValueError('Properties have not been set.')
