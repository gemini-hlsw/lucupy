# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from abc import ABC
from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from typing import FrozenSet

import numpy.typing as npt

from .magnitude import Magnitude
from ..decorators import immutable

TargetName = str


class TargetType(Enum):
    """The type associated with a target in an observation.

    Members:
        - BASE
        - USER
        - BLIND_OFFSET
        - OFF_AXIS
        - TUNING_STAR
        - GUIDESTAR
        - OTHER
    """
    BASE = auto()
    USER = auto()
    BLIND_OFFSET = auto()
    OFF_AXIS = auto()
    TUNING_STAR = auto()
    GUIDESTAR = auto()
    OTHER = auto()


class GuideSpeed(IntEnum):
    """
    How quickly a guider can guide on a guide star.

    Members:
        - SLOW
        - MEDIUM
        - FAST

    """
    SLOW = auto()
    MEDIUM = auto()
    FAST = auto()


class TargetTag(Enum):
    """
    A tag used by nonsidereal targets to indicate their type.
    """
    COMET = auto()
    ASTEROID = auto()
    MAJOR_BODY = auto()


@immutable
@dataclass(frozen=True)
class Target(ABC):
    """
    Basic target information.

    Attributes:
        - name: TargetName
        - magnitudes: Set[Magnitude]
        - type: TargetType
    """
    name: TargetName
    magnitudes: FrozenSet[Magnitude]
    type: TargetType

    def guide_speed(self) -> GuideSpeed:
        """
        Calculate the guide speed for this target.
        """
        ...


@immutable
@dataclass(frozen=True)
class SiderealTarget(Target):
    """
    For a SiderealTarget, we have an RA and Dec and then proper motion information
    to calculate the exact position.

    RA and Dec should be specified in decimal degrees.
    Proper motion must be specified in milliarcseconds / year.
    Epoch must be the decimal year.

    NOTE: The proper motion adjusted coordinates can be found in the TargetInfo in coord.

    Attributes:
        ra (float): Right Ascension
        dec (float): Declination
        pm_ra (float): Proper motion of the right ascension component.
        pm_dec (float): Proper motion of the declination component.
        epoch (float): The epoch in which the ra / dec were measured.

    """
    ra: float
    dec: float
    pm_ra: float
    pm_dec: float
    epoch: float


@immutable
@dataclass(frozen=True)
class NonsiderealTarget(Target):
    """
    For a NonsiderealTarget, we have a HORIZONS designation to indicate the lookup
    information, a tag to determine the type of target, and arrays of ephemerides
    to specify the position.

    Attributes:
        des (str): Horizon designation
        tag (TargetTag): TargetTag
        ra (npt.NDArray[float]): Right Ascension
        dec (npt.NDArray[float]): Declination

    """
    des: str
    tag: TargetTag
    ra: npt.NDArray[float]
    dec: npt.NDArray[float]
