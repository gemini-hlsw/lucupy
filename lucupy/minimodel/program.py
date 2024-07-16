# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, IntEnum, auto
from typing import ClassVar, FrozenSet, List, Optional, final

import numpy as np

from lucupy.decorators import immutable
from lucupy.types import ZeroTime
from lucupy.minimodel.obs_filter import obs_is_not_inactive, obs_is_science_or_progcal

from .group import ROOT_GROUP_ID, Group, Group
from .ids import ObservationID, ProgramID, UniqueGroupID
from .observation import Observation, Priority
from .semester import Semester
from .timeallocation import TimeAllocation, TimeUsed, Band
from .too import TooType

__all__ = [
    # 'Band',
    'Program',
    'ProgramMode',
    'ProgramType',
    'ProgramTypes',
]


@final
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


@final
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


@final
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


@final
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
    thesis: bool
    mode: ProgramMode
    type: Optional[ProgramTypes]
    start: datetime
    end: datetime
    allocated_time: FrozenSet[TimeAllocation] = field(hash=False, compare=False)
    used_time: FrozenSet[TimeUsed] = field(hash=False, compare=False)

    # Root group is immutable and should not be used in hashing or comparisons.
    root_group: Group

    band: Optional[Band] = None
    too_type: Optional[TooType] = None

    FUZZY_BOUNDARY: ClassVar[timedelta] = timedelta(days=14)

    def __post_init__(self):
        if self.root_group.id != ROOT_GROUP_ID:
            raise ValueError(f"Program {self.id.id} should have root group should named {ROOT_GROUP_ID.id}, received: "
                             f'"{self.root_group.id}".')

    def bands(self) -> List[Band]:
        """Unique list of ranking bands, the bands must be included in the allocated_time"""
        seen = set()
        seen_add = seen.add
        return [t.band for t in self.allocated_time if not (t.band in seen or seen_add(t.band))]

    def program_awarded(self) -> timedelta:
        return sum((t.program_awarded for t in self.allocated_time), ZeroTime)

    # ToDo: rename all awarded_used, this is an odd name for previously used time
    # ToDo: used times by band
    def program_awarded_used(self) -> timedelta:
        return sum((t.program_used for t in self.used_time), ZeroTime)

    def partner_awarded(self) -> timedelta:
        return sum((t.partner_awarded for t in self.allocated_time), ZeroTime)

    def partner_awarded_used(self) -> timedelta:
        return sum((t.partner_used for t in self.used_time), ZeroTime)

    def total_awarded(self) -> timedelta:
        return sum((t.total_awarded() for t in self.allocated_time), ZeroTime)

    def total_awarded_used(self) -> timedelta:
        return sum((t.total_used() for t in self.used_time), ZeroTime)

    def program_used(self) -> timedelta:
        return self.root_group.program_used() + self.program_awarded_used()

    def partner_used(self) -> timedelta:
        return self.root_group.partner_used() + self.partner_awarded_used()

    def total_used(self) -> timedelta:
        return self.root_group.total_used() + self.total_awarded_used()

    def not_charged(self) -> timedelta:
        return self.root_group.not_charged() + sum((t.not_charged for t in self.used_time), ZeroTime)

    def observations(self) -> List[Observation]:
        return self.root_group.observations()

    def get_group(self, group_id: UniqueGroupID) -> Optional[Group]:
        """
        Given a UniqueGroupID, find the subgroup with the ID if it exists.
        Returns None if no such group can be found.
        """
        def aux(group: Group) -> Optional[Group]:
            if group.unique_id == group_id:
                return group
            elif not isinstance(group.children, Observation):
                for subgroup in group.children:
                    retval = aux(subgroup)
                    if retval is not None:
                        return retval
            return None

        return aux(self.root_group)

    def get_observation(self, observation_id: ObservationID) -> Optional[Observation]:
        """
        Given an ObservationID, find the Observation with the ID if it exists.
        Returns None if no such Observation can be found.
        """
        def aux(group: Group) -> Optional[Observation]:
            match group.children:
                case Observation():
                    if group.children.id == observation_id:
                        return group.children
                    else:
                        return None
                case _:
                    for subgroup in group.children:
                        check_subgroup = aux(subgroup)
                        if check_subgroup is not None:
                            return check_subgroup
                    return None
        return aux(self.root_group)

    def mean_priority(self) -> float:
        """
        Return the mean user priority from the active SCIENCE and PROGCAL observations.
        This will be a value in the interval [Priority.LOW.value, Priority.HIGH.value] indicating
        the mean over Observations.

        :return: float
        """
        priorities = [obs.priority.value for obs in self.observations()
                      if obs_is_science_or_progcal(obs) and obs_is_not_inactive(obs)]
        return np.mean(priorities) if len(priorities) else Priority.LOW.value

    def show(self):
        """Print content of the Program.
        """
        print(f'Program: {self.id.id}')
        # Print the group and atom information.
        self.root_group.show(1)
