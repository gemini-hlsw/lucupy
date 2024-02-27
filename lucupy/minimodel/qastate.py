# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from enum import IntEnum, auto
from typing import final

__all__ = [
    'QAState',
]


@final
class QAState(IntEnum):
    """
    These correspond to the QA States in the OCS for Observations.
    Entries in the obs log should be made uppercase for lookups into
    this enum.

    PASS is not in original mini-model description, but returned by OCS.

    Members:
        - NONE
        - UNDEFINED
        - FAIL
        - USABLE
        - PASS
        - CHECK

    """
    NONE = auto()
    UNDEFINED = auto()
    FAIL = auto()
    USABLE = auto()
    PASS = auto()
    CHECK = auto()
