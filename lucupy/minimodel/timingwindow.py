# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import ClassVar, Optional

from ..decorators import immutable


@immutable
@dataclass(frozen=True)
class TimingWindow:
    """Representation of timing windows in the mini-model.

    Attributes:
        start (datetime): When a timing window begins.
        duration (timedelta): For infinite duration, set duration to timedelta.max.
        repeat (int):  -1 means forever repeating, 0 means non-repeating.
        period (timedelta, optional): None should be used if repeat < 1.
    """
    start: datetime
    duration: timedelta
    repeat: int
    period: Optional[timedelta]

    # For infinite duration, use the length of an LP.
    INFINITE_DURATION_FLAG: ClassVar[int] = -1
    INFINITE_DURATION: ClassVar[timedelta] = timedelta(days=3 * 365, hours=24)
    FOREVER_REPEATING: ClassVar[int] = -1
    NON_REPEATING: ClassVar[int] = 0
    NO_PERIOD: ClassVar[Optional[timedelta]] = None

    # A number to be used by the Scheduler to represent infinite repeats from the
    # perspective of the OCS: if FOREVER_REPEATING is selected, then it is converted
    # into this for calculation purposes.
    OCS_INFINITE_REPEATS: ClassVar[int] = 1000
