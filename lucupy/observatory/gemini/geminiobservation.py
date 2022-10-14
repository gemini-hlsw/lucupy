# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from datetime import timedelta

from lucupy.minimodel import Observation

from .geminiproperties import GeminiProperties


def with_igrins_cal(func):
    def add_calibration(self):
        if GeminiProperties.Instruments.IGRINS in self.required_resources() and self.partner_used() > 0:
            return func(self) + timedelta(seconds=(1 / 6))
        return func(self)

    return add_calibration


class GeminiObservation(Observation):
    """A Gemini-specific extension of the Observation class.
    """

    @with_igrins_cal
    def total_used(self) -> timedelta:
        """Override total_used method from Observation.

           Adds IGRINS calibration time using a decorator.

        Returns:
            timedelta: Total used time.
        """
        return super().total_used()
