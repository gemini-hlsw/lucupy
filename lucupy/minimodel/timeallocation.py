# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum, IntEnum
from typing import Optional, final

from lucupy.types import ZeroTime

__all__ = [
    'Band',
    'TimeAccountingCode',
    'TimeAllocation',
    'TimeUsed'
]

@final
class Band(IntEnum):
    """
    Program band.
    """
    BAND1 = 1
    BAND2 = 2
    BAND3 = 3
    BAND4 = 4


@final
class TimeAccountingCode(str, Enum):
    """
    The time accounting codes for the possible partner submissions or internal program
    types used at Gemini, also known as categories.

    This will have to be customized for a given observatory if used independently
    of Gemini.
    """
    AR = 'Argentina'
    AU = 'Australia'
    BR = 'Brazil'
    CA = 'Canada'
    CFH = 'CFHT Exchange'
    CL = 'Chile'
    KR = 'Republic of Korea'
    DD = "Director's Time"
    DS = 'Demo Science'
    GS = 'Gemini Staff'
    GT = 'Guaranteed Time'
    JP = 'Subaru'
    LP = 'Large Program'
    LTP = 'Limited-term Participant'
    SV = 'System Verification'
    UH = 'University of Hawaii'
    UK = 'United Kingdom'
    US = 'United States'
    XCHK = 'Keck Exchange'

@final
class GppTimeAccountingCode(str, Enum):
    """
    The time accounting codes for the possible partner submissions or internal program
    types used at Gemini, also known as categories.
    This is for if the GPP codes differ substantially from OCS.

    This will have to be customized for a given observatory if used independently
    of Gemini.
    """
    AR = 'Argentina'
    AU = 'Australia'
    BR = 'Brazil'
    CA = 'Canada'
    CFH = 'CFHT Exchange'
    CL = 'CL'
    KR = 'Republic of Korea'
    DD = "Director's Time"
    DS = 'Demo Science'
    GS = 'Gemini Staff'
    GT = 'Guaranteed Time'
    JP = 'Subaru'
    LP = 'Large Program'
    LTP = 'Limited-term Participant'
    SV = 'System Verification'
    UH = 'University of Hawaii'
    UK = 'United Kingdom'
    US = 'United States'
    XCHK = 'Keck Exchange'


@final
@dataclass
class TimeAllocation:
    """
    Time allocation information for a given category for a program.
    Programs may be sponsored by multiple categories with different amounts
    of time awarded. This class maintains information about the time awarded
    and the time that has been used, divided between program time and partner
    calibration time. The time used is calculated as a ratio of the awarded time
    for this category to the total time awarded to the program.

    Attribute:
        category (TimeAccountingCode):
        program_awarded (timedelta):
        partner_awarded (timedelta):
        band (Band)
    """
    category: TimeAccountingCode
    program_awarded: timedelta
    partner_awarded: timedelta
    band: Optional[Band] = None

    def total_awarded(self) -> timedelta:
        return self.program_awarded + self.partner_awarded

    def __hash__(self):
        return self.category.__hash__()


@final
@dataclass
class TimeUsed:
    """
    Time charged information for a given category for a program.

    Attribute:
        program_used (timedelta):
        partner_used (timedelta):
        not_charged (timedelta):
        band (Band)
    """
    program_used: timedelta
    partner_used: timedelta
    not_charged: timedelta
    # band: Band

    def total_used(self) -> timedelta:
        return self.program_used + self.partner_used

    # ToDo: hash on the band once available
    def __hash__(self):
        return self.program_used.__hash__()
