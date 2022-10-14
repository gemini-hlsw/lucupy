# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from enum import IntEnum, auto


class TooType(IntEnum):
    """
    The target-of-opportunity type for a program and for an observation.
    These are ordered specifically so that we can compare them.

    The INTERRUPT is considered the highest level of TooType, followed by RAPID, and then STANDARD.

    Thus, a Program with a RAPID type, for example, can contain RAPID and STANDARD Observations,
    but not INTERRUPT ones.

    The values and ordering on them should NOT be changed as this will break functionality.

    Members:
        - STANDARD
        - RAPID
        - INTERRUPT

    """
    STANDARD = auto()
    RAPID = auto()
    INTERRUPT = auto()
