# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from .observation import Observation, ObservationClass, ObservationStatus


__all__ = [
    'obs_is_science_or_progcal',
    'obs_is_not_inactive',
]


_OBS_CLASSES = frozenset({ObservationClass.SCIENCE, ObservationClass.PROGCAL})


def obs_is_science_or_progcal(obs: Observation) -> bool:
    """
    Return True if the Observation is a SCIENCE or PROGCAL observation.
    :param obs: the Observation to check
    :return: True if the Observation is a SCIENCE or PROGCAL observation and False otherwise
    """
    return obs.obs_class in _OBS_CLASSES


def obs_is_not_inactive(obs: Observation) -> bool:
    """
    Return True if the Observation is not INACTIVE.
    :param obs: the Observation to check
    :return: True if Observation is not INACTIVE and False otherwise
    """
    return obs.status != ObservationStatus.INACTIVE
