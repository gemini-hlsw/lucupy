# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class ID(ABC):
    id: str

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id})'


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
    ...
