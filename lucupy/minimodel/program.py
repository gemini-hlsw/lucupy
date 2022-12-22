# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, IntEnum, auto
from typing import ClassVar, FrozenSet, List, Optional

from .group import AndGroup, Group, ROOT_GROUP_ID
from .ids import ProgramID, GroupID
from .observation import Observation
from .semester import Semester
from .timeallocation import TimeAllocation
from .too import TooType
from ..decorators import immutable
from ..types import ZeroTime


class Band(IntEnum):
    """
    Program band.
    """
    BAND1 = 1
    BAND2 = 2
    BAND3 = 3
    BAND4 = 4


class ProgramMode(IntEnum):
    """
    Main operational mode, which is one of:
    * Queue
    * Classical
    * Priority Visitor (hybrid mode between queue and classical)
    """
    QUEUE = auto()
    CLASSICAL = auto()
    PV = auto()


@immutable
@dataclass(frozen=True)
class ProgramType:
    """
    Represents the information encompassing the type of program.
    * abbreviation: the code used by the program type (e.g. Q, C, FT, LP)
    * name: user readable representation of the program type
    * is_science: indicates if this program type is a science program

    NOTE that ProgramType instances should NEVER be explicitly created.
    All of the valid ProgramType instances are contained in the ProgramTypes enum
    and should be accessed from there.
    """
    abbreviation: str
    name: str
    is_science: bool = True


class ProgramTypes(Enum):
    """
    A complete list of the ProgramType instances used by Gemini.
    As mentioned in ProgramType, ProgramType should never be instantiated
    outside of this enum: instead, ProgramType instances should be retrieved
    from here.
    """
    C = ProgramType('C', 'Classical')
    CAL = ProgramType('CAL', 'Calibration', False)
    DD = ProgramType('DD', "Director's Time")
    DS = ProgramType('DS', 'Demo Science')
    ENG = ProgramType('ENG', 'Engineering', False)
    FT = ProgramType('FT', 'Fast Turnaround')
    LP = ProgramType('LP', 'Large Program')
    Q = ProgramType('Q', 'Queue')
    SV = ProgramType('SV', 'System Verification')


@dataclass
class Program:
    """
    Representation of a program.

    The FUZZY_BOUNDARY is a constant that allows for a fuzzy boundary for a program's
    start and end times.
    """
    id: ProgramID
    internal_id: str
    # Some programs do not have a typical name and thus cannot be associated with a semester.
    semester: Optional[Semester]
    band: Band
    thesis: bool
    mode: ProgramMode
    type: Optional[ProgramTypes]
    start: datetime
    end: datetime
    allocated_time: FrozenSet[TimeAllocation] = field(hash=False, compare=False)

    # Root group is immutable and should not be used in hashing or comparisons.
    root_group: AndGroup

    too_type: Optional[TooType] = None

    FUZZY_BOUNDARY: ClassVar[timedelta] = timedelta(days=14)

    def __post_init__(self):
        if self.root_group.id != ROOT_GROUP_ID:
            raise ValueError(f"A Program's root group should be named {ROOT_GROUP_ID}, received: "
                             f'"{self.root_group.id}".')

    def program_awarded(self) -> timedelta:
        return sum((t.program_awarded for t in self.allocated_time), ZeroTime)

    def program_awarded_used(self) -> timedelta:
        return sum((t.program_used for t in self.allocated_time), ZeroTime)

    def partner_awarded(self) -> timedelta:
        return sum((t.partner_awarded for t in self.allocated_time), ZeroTime)

    def partner_awarded_used(self) -> timedelta:
        return sum((t.partner_used for t in self.allocated_time), ZeroTime)

    def total_awarded(self) -> timedelta:
        return sum((t.total_awarded() for t in self.allocated_time), ZeroTime)

    def total_awarded_used(self) -> timedelta:
        return sum((t.total_used() for t in self.allocated_time), ZeroTime)

    def program_used(self) -> timedelta:
        return self.root_group.program_used()

    def partner_used(self) -> timedelta:
        return self.root_group.partner_used()

    def total_used(self) -> timedelta:
        return self.root_group.total_used()

    def observations(self) -> List[Observation]:
        return self.root_group.observations()

    def get_group_ids(self) -> FrozenSet[GroupID]:
        return self.root_group.subgroup_ids()

    def get_group(self, group_id: GroupID) -> Optional[Group]:
        def aux(group: Group) -> Optional[Group]:
            if group.id == group_id:
                return group
            elif group.is_scheduling_group():
                for subgroup in group.children:
                    retval = aux(subgroup)
                    if retval is not None:
                        return retval
            return None

        return aux(self.root_group)

    def show(self):
        """Print content of the Program.
        """
        print(f'Program: {self.id}')
        # Print the group and atom information.
        self.root_group.show(1)
