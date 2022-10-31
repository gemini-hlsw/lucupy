# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum, auto
from typing import FrozenSet, List, NoReturn, Optional, Union

from lucupy.helpers import flatten

from .constraints import Constraints
from .observation import Observation
from .resource import Resource
from .site import Site

GroupID = str


@dataclass
class Group(ABC):
    """This is the base implementation of AND / OR Groups.
    Python does not allow classes to self-reference unless in static contexts,
    so we make a very simple base class to self-reference from subclasses since
    we need this functionality to allow for group nesting.


    Attributes:
        id (GroupID): the identification of the group.
        group_name (str): a human-readable name of the group.
        number_to_observe (int): the number of children in the group that must be observed for the group to be considered complete.
        delay_min(timedelta): used in cadences.
        delay_ma(timedelta): used in cadences.
        children (Union[List['Group'], Observation]): member(s) of the group
    """
    id: GroupID
    group_name: str
    number_to_observe: int
    delay_min: timedelta
    delay_max: timedelta
    children: Union[List['Group'], Observation]

    def __post_init__(self):
        if self.number_to_observe <= 0:
            msg = f'Group {self.group_name} specifies non-positive {self.number_to_observe} children to be observed.'
            raise ValueError(msg)

    def subgroup_ids(self) -> FrozenSet[GroupID]:
        """Get the ids for all the sub-groups inside.

        Returns:
            FrozenSet[GroupID]: Set of GroupID values.
        """
        if isinstance(self.children, Observation):
            return frozenset()
        else:
            return frozenset(subgroup.id for subgroup in self.children)

    def sites(self) -> FrozenSet[Site]:
        """All belonging Sites.

        Returns:
            FrozenSet[Site]: Set of Sites for all observations.
        """
        if isinstance(self.children, Observation):
            return frozenset([self.children.site])
        else:
            return frozenset.union(*[s.sites() for s in self.children])

    def required_resources(self) -> FrozenSet[Resource]:
        """
        Returns:
            FrozenSet[Resource]: A set of Resources.
        """
        return frozenset(r for c in self.children for r in c.required_resources())

    def wavelengths(self) -> FrozenSet[float]:
        """
        Returns:
            FrozenSet[float]: A set of wavelengths.
        """
        return frozenset(w for c in self.children for w in c.wavelengths())

    def constraints(self) -> FrozenSet[Constraints]:
        """
        Returns:
            FrozenSet[Constraints]: All set of Constraints in the group.
        """
        return frozenset(cs for c in self.children for cs in c.constraints())

    def observations(self) -> List[Observation]:
        """
        Returns:
            List[Observation]: A set of Observations.
        """
        if isinstance(self.children, Observation):
            return [self.children]
        else:
            return [o for g in self.children for o in g.observations()]

    def is_observation_group(self) -> bool:
        """
        Returns:
            bool: True if the group is just a single Observation, otherwise False.
        """
        return issubclass(type(self.children), Observation)

    def is_scheduling_group(self) -> bool:
        """
        Returns:
            bool: True if the group is a scheduling group, otherwise False.
        """
        return not (self.is_observation_group())

    def exec_time(self) -> timedelta:
        """Total execution time across the children of this group.

        Returns:
            exec_time (timedelta): Sum of all the execution times.
        """
        if issubclass(type(self.children), Observation):
            return self.children.exec_time()
        else:
            sum(child.exec_time() for child in self.children)

    def program_used(self) -> timedelta:
        """Program time used across the group.

        Returns:
            program_used (timedelta): Sum of all program_used times across children of this group.
        """
        if issubclass(type(self.children), Observation):
            return self.children.program_used()
        else:
            return sum(child.program_used() for child in self.children)

    def partner_used(self) -> timedelta:
        """Partner time used across the group.

        Returns:
            partner_time (timedelta): Sum of all `partner_used` across the children of this group.
        """
        if issubclass(type(self.children), Observation):
            return self.children.partner_used()
        else:
            return sum(child.partner_used() for child in self.children)

    def total_used(self) -> timedelta:
        """Total time used across the group: includes program time and partner time.

        Returns:
            total_used (timedelta): Sum of total_used times across all children.
        """
        if issubclass(type(self.children), Observation):
            return self.children.total_used()
        else:
            return sum(child.total_used() for child in self.children)

    def show(self, depth: int = 1) -> NoReturn:
        """Print content of the Group.

        Args:
            depth (int, optional): depth of the separator. Defaults to 1.
        """
        def sep(indent: int) -> str:
            return '----- ' * indent
        # Is this a subgroup or an observation?
        if isinstance(self.children, Observation):
            self.children.show(depth)
        elif isinstance(self.children, list):
            print(f'{sep(depth)} Group: {self.id}')
            for child in self.children:
                child.show(depth + 1)

    @abstractmethod
    def is_and_group(self) -> bool:
        ...

    @abstractmethod
    def is_or_group(self) -> bool:
        ...

    def __len__(self):
        return 1 if self.is_observation_group() else len(self.children)


class AndOption(Enum):
    """
    Different options available for ordering AND group children.
    CUSTOM is used for cadences.

    Members:
       - CONSEC_ORDERED
       - CONSEC_ANYORDER
       - NIGHT_ORDERED
       - NIGHT_ANYORDER
       - ANYORDER
       - CUSTOM
    """
    CONSEC_ORDERED = auto()
    CONSEC_ANYORDER = auto()
    NIGHT_ORDERED = auto()
    NIGHT_ANYORDER = auto()
    ANYORDER = auto()
    CUSTOM = auto()


@dataclass
class AndGroup(Group):
    """The concrete implementation of an AND group.

    Attributes:
        group_option (AndOption): Specify how its observations should be handled.
        previous (int, optional): An index into the group's children to indicate the previously observed child,
            or None if none of the children have yet been observed. Default to None.

    """
    group_option: AndOption
    previous: Optional[int] = None

    def __post_init__(self):
        super().__post_init__()
        if self.number_to_observe != len(self.children):
            msg = f'AND group {self.group_name} specifies {self.number_to_observe} children to be observed but has ' \
                  f'{len(self.children)} children.'
            raise ValueError(msg)
        if self.previous is not None and (self.previous < 0 or self.previous >= len(self.children)):
            msg = f'AND group {self.group_name} has {len(self.children)} children and an illegal previous value of ' \
                  f'{self.previous}'
            raise ValueError(msg)

    def is_and_group(self) -> bool:
        return True

    def is_or_group(self) -> bool:
        return False

    def instruments(self) -> FrozenSet[Resource]:
        """
        Returns:
            instruments (FrozenSet[Resource]): A set of all instruments used in this group.
        """
        if issubclass(type(self.children), Observation):
            instrument = self.children.instrument()
            if instrument is not None:
                return frozenset({instrument})
            else:
                return frozenset()
        else:
            return frozenset(flatten([child.instruments() for child in self.children]))


@dataclass
class OrGroup(Group):
    """
    The concrete implementation of an OR group.
    The restrictions on an OR group is that it must explicitly require not all
    of its children to be observed.
    """

    def __post_init__(self):
        super().__post_init__()
        if self.number_to_observe >= len(self.children):
            msg = f'OR group {self.group_name} specifies {self.number_to_observe} children to be observed but has ' \
                  f'{len(self.children)} children.'
            raise ValueError(msg)

    def is_and_group(self) -> bool:
        return False

    def is_or_group(self) -> bool:
        return True
