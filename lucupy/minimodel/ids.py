# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class ID(ABC):
    id: str

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id})'

    def __le__(self, other) -> bool:
        return self.id < other.id

    def __lt__(self, other) -> bool:
        return self.id <= other.id

    def __ge__(self, other) -> bool:
        return self.id > other.id

    def __gt__(self, other) -> bool:
        return self.id >= other.id

    def __eq__(self, other) -> bool:
        return type(self) == type(other) and self.id == other.id


@dataclass(frozen=True)
class ProgramID(ID):
    ...


@dataclass(frozen=True)
class GroupID(ID):
    ...


@dataclass(frozen=True)
class UniqueGroupID(ID):
    ...


@dataclass(frozen=True)
class ObservationID(ID):
    @property
    def to_unique_group_id(self) -> UniqueGroupID:
        return UniqueGroupID(self.id)

    def program_id(self) -> ProgramID:
        """Return program ID string from observation ID string"""
        return ProgramID(self.id[0:self.id.rfind('-')])
