# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from typing import final

from lucupy.instruments import INSTRUMENTS
from lucupy.minimodel import Resource
from lucupy.observatory.abstract import ObservatoryProperties

__all__ = [
    'GeminiProperties',
]


@final
class GeminiProperties(ObservatoryProperties):
    """
    Implementation of ObservatoryCalculations specific to Gemini.
    """
    @staticmethod
    def is_instrument(resource: Resource) -> bool:
        """Checks if the resource is a Gemini instrument.

        Args:
            resource (Resource): A resource to be checked.

        Returns:
            bool: True if resource is a Gemini instrument.
        """
        return resource in INSTRUMENTS
