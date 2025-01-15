# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum, auto
from typing import Final, FrozenSet, List, Optional, Callable

from lucupy.helpers import flatten
from lucupy.minimodel.constraints import Constraints
from lucupy.minimodel.ids import (GroupID, ObservationID, ProgramID,
                                  UniqueGroupID)
from lucupy.minimodel.obs_filter import obs_is_not_inactive, obs_is_science_or_progcal
from lucupy.minimodel.observation import Observation, ObservationClass, Priority
from lucupy.minimodel.resource import Resources
from lucupy.minimodel.site import Site
from lucupy.minimodel.wavelength import Wavelengths

from .observationmode import ObservationMode

__all__ = [
    # 'AndGroup',
    'AndOption',
    'BaseGroup',
    # 'OrGroup',
    'Group',
    'ROOT_GROUP_ID',
]

ROOT_GROUP_ID: Final[GroupID] = GroupID('root')


@dataclass
class BaseGroup(ABC):
    """This is the base implementation of AND / OR Groups.
    Python does not allow classes to self-reference unless in static contexts,
    so we make a very simple base class to self-reference from subclasses since
    we need this functionality to allow for group nesting.


    Attributes:
        id (GroupID): the identifier of the group.
        program_id (ProgramID): the identifier of the program to which this group belongs.
        group_name (str): a human-readable name of the group.
        number_to_observe (int): the number of children in the group that must be observed for the group to be
                                 considered complete.
        delay_min(timedelta): used in cadences.
        delay_max(timedelta): used in cadences.
        children (Union[List[Group], Observation]): member(s) of the group
    """
    id: GroupID
    program_id: ProgramID
    group_name: str
    number_to_observe: int
    delay_min: timedelta
    delay_max: timedelta
    children: List[Group] | Observation

    # Calculated afterward.
    unique_id: UniqueGroupID = field(init=False)

    def __post_init__(self):
        if self.number_to_observe <= 0:
            msg = f'Group {self.group_name} specifies non-positive {self.number_to_observe} children to be observed.'
            raise ValueError(msg)

        if self.id.id.startswith(self.program_id.id):
            unique_id = self.id.id
        else:
            unique_id = f'{self.program_id.id}:{self.id.id}'
        object.__setattr__(self, 'unique_id', UniqueGroupID(unique_id))

    def subgroup_ids(self) -> FrozenSet[GroupID]:
        """Get the ids for all the subgroups inside. This should probably not be used.

        Returns:
            FrozenSet[GroupID]: Consists of all the GroupID for Groups (exclusive) rooted here.
        """
        if isinstance(self.children, Observation):
            return frozenset()

        # Add the IDs of the children and traverse the tree.
        ids = set()
        for sg in self.children:
            ids |= {sg.id} | sg.subgroup_ids()
        return frozenset(ids)

    def subgroup_unique_ids(self) -> FrozenSet[UniqueGroupID]:
        """Get all the unique ids for all the subgroups inside.

        Returns:
            FrozenSet[UniqueGroupID]: Consists of all the UniqueGroupID for Groups (exclusive) rooted here.
        """
        if isinstance(self.children, Observation):
            return frozenset()

        # Add the IDs of the children and traverse the tree.
        ids = set()
        for sg in self.children:
            ids |= {sg.unique_id} | sg.subgroup_unique_ids()
        return frozenset(ids)

    def sites(self) -> FrozenSet[Site]:
        """All belonging Sites.

        Returns:
            FrozenSet[Site]: Set of Sites for all observations.
        """
        if isinstance(self.children, Observation):
            return frozenset([self.children.site])
        else:
            return frozenset.union(*[s.sites() for s in self.children])

    def required_resources(self) -> Resources:
        """
        Returns:
            Resources: A set of Resources.
        """
        if isinstance(self.children, Observation):
            return self.children.required_resources()
        else:
            return frozenset(r for c in self.children for r in c.required_resources())

    def wavelengths(self) -> Wavelengths:
        """
        Returns:
            Wavelengths: A set of wavelengths.
        """
        if isinstance(self.children, Observation):
            return self.children.wavelengths()
        else:
            return frozenset(w for c in self.children for w in c.wavelengths())

    def constraints(self) -> List[Constraints]:
        """
        Returns:
            List[Constraints]: All set of Constraints of children in the group.
        """
        if isinstance(self.children, Observation):
            return [self.children.constraints]
        else:
            return [cs for c in self.children for cs in c.constraints()]

    def observations(self) -> List[Observation]:
        """
        Returns:
            List[Observation]: A list of Observations.
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
        return not self.is_observation_group()

    @property
    def to_observation_id(self) -> ObservationID:
        """
        A method that, for observation groups, returns the corresponding ObservationID for the observation contained
        in the group

        If the group is instead a scheduling group, a TypeError will be raised.
        """
        if self.is_observation_group():
            if isinstance(self.children, Observation):
                return self.children.id
            else:
                raise TypeError('Failed is_observation_group method')
        else:
            raise TypeError('Cannot get an ObservationID from a scheduling group.')


    def not_charged(self) -> timedelta:
        """not_charged time across the group.

        Returns:
            not_charged (timedelta): Sum of all `not_charged` across the children of this group.
        """
        if isinstance(self.children, Observation):
            return self.children.not_charged()
        else:
            return sum((child.not_charged() for child in self.children), timedelta())

    def _filtered_obs_list(self, obs_filter: Callable[[Observation], bool]) -> List[Observation]:
        return [obs for obs in self.observations() if obs_filter(obs)]

    def program_observations(self) -> List[Observation]:
        """Return the list of program (science + program calibration) observations in the group"""
        return self._filtered_obs_list(obs_is_science_or_progcal)

    def partner_observations(self) -> List[Observation]:
        """Return the list of partner calibration observations in the group"""
        return self._filtered_obs_list(lambda obs: obs.obs_class == ObservationClass.PARTNERCAL)

    def daycal_observations(self) -> List[Observation]:
        """Return the list of daytime calibration observations in the group"""
        return self._filtered_obs_list(lambda obs: obs.obs_class == ObservationClass.DAYCAL)

    def obs_class(self) -> ObservationClass:
        """
        Determine a group 'obs_class' for observation groups
        """
        obs_class = ObservationClass.NONE
        if self.is_and_group():
            if isinstance(self.children, Observation):
                obs_class = self.children.obs_class
            else:
                obs_class = min(child.obs_class() for child in self.children)
        return obs_class

    def obs_mode(self) -> ObservationMode:
        """
        Return an observation mode based on those of the children
        TODO: Consider the case of mixed imaging and spectroscopy groups, maybe this should return a list
        :return:
        """
        obs_mode = ObservationMode.UNKNOWN
        if self.is_and_group():
            if isinstance(self.children, Observation):
                obs_mode = self.children.obs_mode()
            else:
                obs_mode = max(child.obs_mode() for child in self.children)
        return obs_mode

    def priority(self) -> Priority:
        """
        Return the maximum user priority based on those of the children Observations
        for active Observations where the ObservationClass is SCIENCE or PROGCAL.
        If there is no such Observation, Priority.LOW is returned.

        :return: priority
        """
        priority = Priority.LOW
        if self.is_and_group():
            if isinstance(self.children, Observation):
                obs = self.children
                priority = obs.priority if obs_is_science_or_progcal(obs) and obs_is_not_inactive(obs) else Priority.LOW
            else:
                # This should always work because the leaves will always be an Observation.
                priority = max(child.priority() for child in self.children)
        return priority

    def show(self, depth: int = 1) -> None:
        """Print content of the Group.

        Args:
            depth (int, optional): depth of the separator. Defaults to 1.
        """
        def sep(indent: int) -> str:
            return '-----' * indent

        # Is this a subgroup or an observation?
        group_type = 'Scheduling Group' if self.is_scheduling_group() else 'Observation Group'
        print(f'{sep(depth)} Group: {self.id.id}, unique_id={self.unique_id.id} '
              f'({group_type}, num_children={len(self.children)})')
        if isinstance(self.children, Observation):
            self.children.show(depth + 1)
        else:
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
    NONE = auto()


# @dataclass
# class AndGroup(BaseGroup):
#     """The concrete implementation of an AND group.
#
#     Attributes:
#         group_option (AndOption): Specify how its observations should be handled.
#         previous (int, optional): An index into the group's children to indicate the previously observed child,
#             or None if none of the children have yet been observed. Default to None.
#
#     """
#     group_option: AndOption
#     previous: Optional[int] = None
#
#     def __post_init__(self):
#         super().__post_init__()
#         if self.number_to_observe != len(self.children):
#             msg = f'AND group {self.group_name} specifies {self.number_to_observe} children to be observed but has ' \
#                   f'{len(self.children)} children.'
#             raise ValueError(msg)
#         if self.previous is not None and (self.previous < 0 or self.previous >= len(self.children)):
#             msg = f'AND group {self.group_name} has {len(self.children)} children and an illegal previous value of ' \
#                   f'{self.previous}'
#             raise ValueError(msg)
#
#     def is_and_group(self) -> bool:
#         return True
#
#     def is_or_group(self) -> bool:
#         return False
#
#     def instruments(self) -> Resources:
#         """
#         Returns:
#             instruments (Resources): A set of all instruments used in this group.
#         """
#         if isinstance(self.children, Observation):
#             instrument = self.children.instrument()
#             if instrument is not None:
#                 return frozenset({instrument})
#             else:
#                 return frozenset()
#         else:
#             return frozenset(flatten([child.instruments() for child in self.children]))  # type: ignore
#
#
# @dataclass
# class OrGroup(BaseGroup):
#     """
#     The concrete implementation of an OR group.
#     The restrictions on an OR group is that it must explicitly require not all
#     of its children to be observed.
#     """
#
#     def __post_init__(self):
#         super().__post_init__()
#         if self.number_to_observe >= len(self.children):
#             msg = f'OR group {self.group_name} specifies {self.number_to_observe} children to be observed but has ' \
#                   f'{len(self.children)} children.'
#             raise ValueError(msg)
#
#     def is_and_group(self) -> bool:
#         return False
#
#     def is_or_group(self) -> bool:
#         return True


@dataclass
class Group(BaseGroup):
    """The concrete implementation of a group, combines AND/OR properties and supports GPP

    Attributes:
        group_option (AndOption): Specify how its observations should be handled.
        previous (int, optional): An index into the group's children to indicate the previously observed child,
            or None if none of the children have yet been observed. Default to None.
        parent_id (GroupID, optional): Id of the parent, for GPP
        parent_index (int, optional) = Index of the parent group, for GPP

    """
    group_option: AndOption
    previous: Optional[int] = None
    parent_id: Optional[GroupID] = GroupID('')
    parent_index: Optional[int] = None

    def __post_init__(self):
        super().__post_init__()
        if self.group_option == AndOption.NONE and self.number_to_observe > len(self.children):
            msg = f'OR group {self.group_name} specifies {self.number_to_observe} children to be observed but has ' \
                  f'{len(self.children)} children.'
            raise ValueError(msg)
        # if self.group_option != AndOption.NONE and self.number_to_observe != len(self.children):
        #     msg = f'AND group {self.group_name} specifies {self.number_to_observe} children to be observed but has ' \
        #           f'{len(self.children)} children.'
        #     raise ValueError(msg)
        if self.previous is not None and (self.previous < 0 or self.previous >= len(self.children)):
            msg = f'AND group {self.group_name} has {len(self.children)} children and an illegal previous value of ' \
                  f'{self.previous}'
            raise ValueError(msg)

    def instruments(self) -> Resources:
        """
        Returns:
            instruments (Resources): A set of all instruments used in this group.
        """
        if isinstance(self.children, Observation):
            instrument = self.children.instrument()
            if instrument is not None:
                return frozenset({instrument})
            else:
                return frozenset()
        else:
            return frozenset(flatten([child.instruments() for child in self.children]))  # type: ignore

    def is_and_group(self) -> bool:
        return True if self.group_option != AndOption.NONE else False

    def is_or_group(self) -> bool:
        return True if self.group_option == AndOption.NONE and self.number_to_observe <= len(self.children) else False