# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from dataclasses import dataclass
from datetime import timedelta
from enum import IntEnum, auto
from typing import FrozenSet, List, Mapping, NoReturn, Optional

from lucupy.observatory.abstract import ObservatoryProperties

from .atom import Atom
from .constraints import Constraints
from .ids import ObservationID
from .qastate import QAState
from .resource import Resource
from .site import Site
from .target import Target, TargetType
from .too import TooType
from ..types import ZeroTime


class ObservationStatus(IntEnum):
    """
    The status of an observation as indicated in the Observing Tool / ODB.

    Members:
        - NEW
        - INCLUDED
        - PROPOSED
        - APPROVED
        - FOR_REVIEW: Not in original mini-model description, but returned by OCS.
        - ON_HOLD
        - READY
        - ONGOING
        - OBSERVED
        - INACTIVE
        - PHASE2
    """
    NEW = auto()
    INCLUDED = auto()
    PROPOSED = auto()
    APPROVED = auto()
    FOR_REVIEW = auto()
    ON_HOLD = auto()
    READY = auto()
    ONGOING = auto()
    OBSERVED = auto()
    INACTIVE = auto()
    PHASE2 = auto()


class Priority(IntEnum):
    """An observation's priority.
    Note that these are ordered specifically so that we can compare them.

    Members:
        - LOW
        - MEDIUM
        - HIGH
    """
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


class SetupTimeType(IntEnum):
    """The setup time type for an observation.

    Members:
        - NONE
        - REACQUISITION
        - FULL
    """
    NONE = auto()
    REACQUISITION = auto()
    FULL = auto()


class ObservationClass(IntEnum):
    """The class of an observation.

    Note that the order of these is specific and deliberate: they are listed in
    preference order for observation classes, and hence, should not be rearranged.
    These correspond to the values in the OCS when made uppercase.

    Members:
        - SCIENCE
        - PROGCAL
        - PARTNERCAL
        - ACQ
        - ACQCAL
        - DAYCAL

    """
    SCIENCE = auto()
    PROGCAL = auto()
    PARTNERCAL = auto()
    ACQ = auto()
    ACQCAL = auto()
    DAYCAL = auto()


@dataclass
class Observation:
    """Representation of an observation.
    Non-obvious fields are documented below.
    Attributes:
        id (ObservationID): should represent the observation's ID, e.g. GN-2018B-Q-101-123.
        internal_id (str): is the key associated with the observation
        order (int): refers to the order of the observation in either its group or the program
        title (str):
        site (site): the Site in which the Observation has to be done.
        status (ObservationStatus):
        active (bool): Indicates if the Observation is active or not.
        priority(Priority): Priority of the Observation. Affects the scoring.
        setuptime_type(SetupTimeType): When doing / resuming an Observation,
            indicates if a reacquisition, a full setup or just nothing has to be done.
        acq_overhead (timedelta): Time overhead for acquisition.
        obs_class (ObservationClass): Type of Observation.
        targets (List[Target]): should contain a complete list of all targets associated with the observation,
            with the base being in the first position
        guiding (Mapping[Resource, Target]): is a map between guide probe resources and their targets.
        sequence (List[Atom]): Sequence of Atoms that describe the observation.
        constraints (Constraints, optional): Some observations do not have constraints, e.g. GN-208A-FT-103-6.
        too_type (TooType, optional): Default to None.

    """
    id: ObservationID
    internal_id: str
    order: int
    title: str
    site: Site
    status: ObservationStatus
    active: bool
    priority: Priority
    setuptime_type: SetupTimeType
    acq_overhead: timedelta

    # TODO: This will be handled differently between OCS and GPP.
    # TODO: 1. In OCS, when the sequence is examined, the ObservationClasses of the
    # TODO:    individual observes (sequence steps) will be analyzed and the highest
    # TODO:    precedence one will be set for the observation (based on the earliest
    # TODO:    ObservationClass in the enum).
    # TODO: 2. In GPP, this information will be handled automatically and require no
    # TODO:    special processing.
    # TODO: Should this be Optional?
    obs_class: ObservationClass

    targets: List[Target]
    guiding: Mapping[Resource, Target]
    sequence: List[Atom]

    # Some observations do not have constraints, e.g. GN-208A-FT-103-6.
    constraints: Optional[Constraints]

    too_type: Optional[TooType] = None

    def base_target(self) -> Optional[Target]:
        """
        Returns:
            Get the base target for this Observation if it has one, and None otherwise.
        """
        return next(filter(lambda t: t.type == TargetType.BASE, self.targets), None)

    def exec_time(self) -> timedelta:
        """
        Returns:
            Total execution time for the program, which is the sum across atoms and the acquisition overhead.
        """
        return sum((atom.exec_time for atom in self.sequence), ZeroTime) + self.acq_overhead

    def total_used(self) -> timedelta:
        """
        Returns:
            Total program time used: includes program time and partner time.
        """
        return self.program_used() + self.partner_used()

    def required_resources(self) -> FrozenSet[Resource]:
        """
        Returns:
            The required resources for an observation based on the sequence's needs.
        """
        # TODO: For now, we do not return guiding keys amongst the resources.
        # return frozenset(self.guiding.keys() | {r for a in self.sequence for r in a.resources})
        return frozenset((r for a in self.sequence for r in a.resources))

    def instrument(self) -> Optional[Resource]:
        """
        Returns:
            A resource that is an instrument, if one exists. There should be only one.
        """
        return next(filter(lambda r: ObservatoryProperties.is_instrument(r),
                           self.required_resources()), None)

    def wavelengths(self) -> FrozenSet[float]:
        """
        Returns:
            The set of wavelengths included in the sequence.
        """
        return frozenset((w for c in self.sequence for w in c.wavelengths))

    def constraints(self) -> FrozenSet[Constraints]:
        """
        Returns:
            A set of the constraints required by the observation.
            In the case of an observation, this is just the (optional) constraints.
        """
        return frozenset([self.constraints] if self.constraints is not None else [])

    def program_used(self) -> timedelta:
        """We roll this information up from the atoms as it will be calculated
            during the Optimizer algorithm. Note that it is also available directly
            from the OCS, which is used to populate the time allocation.
        Returns:
            (timedelta): With the time program used.
        """
        return sum((atom.prog_time for atom in self.sequence), start=ZeroTime)

    def partner_used(self) -> timedelta:
        """We roll this information up from the atoms as it will be calculated
        during the Optimizer algorithm. Note that it is also available directly
        from the OCS, which is used to populate the time allocation.

        Returns:
            (timedelta): With the time program used.
        """
        return sum((atom.part_time for atom in self.sequence), start=ZeroTime)

    @staticmethod
    def _select_obsclass(classes: List[ObservationClass]) -> Optional[ObservationClass]:
        """Given a list of non-empty ObservationClasses, determine which occurs with
        highest precedence in the ObservationClasses enum, i.e. has the lowest index.

        This will be used when examining the sequence for atoms.

        Returns:
            (ObservationClass): Lowest-index ObservationClasses or None if the list is empty.
        """
        # TODO: Move this to the ODB program extractor as the logic is used there.
        # TODO: Remove from Bryan's atomizer.
        return min(classes, default=None)

    @staticmethod
    def _select_qastate(qastates: List[QAState]) -> Optional[QAState]:
        """
        Given a list of non-empty QAStates, determine which occurs with
        highest precedence in the QAStates enum, i.e. has the lowest index.

        Returns:
            (QAState): Lowest-index QAStates or None if the list is empty.
        """
        # TODO: Move this to the ODB program extractor as the logic is used there.
        # TODO: Remove from Bryan's atomizer.

        return min(qastates, default=None)

    def show(self, depth: int = 1) -> NoReturn:
        """Print content of the Observation.

        Args:
            depth (int, optional): depth of the separator. Defaults to 1.
        """
        def sep(indent: int) -> str:
            return '-----' * indent

        print(f'{sep(depth)} Observation: {self.id}')
        for atom in self.sequence:
            print(f'{sep(depth + 1)} {atom}')

    def __len__(self):
        """
        This is to treat observations the same as groups and is a bit of a hack.
        Observations are to be placed in AND Groups of size 1 for scheduling purposes.
        """
        return 1

    def __eq__(self, other: 'Observation') -> bool:
        """
        We override the equality checker created by @dataclass to temporarily skip sequence
        comparison in test cases until the atom creation process is finish.
        """

        return (dict((k, v) for k, v in self.__dict__.items() if k != 'sequence') ==
                dict((k, v) for k, v in other.__dict__.items() if k != 'sequence'))
