# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from datetime import timedelta
from typing import Callable, Final, Generic, List, TypeAlias, TypeVar
from enum import auto, Enum

import numpy.typing as npt
from astropy.time import Time

T = TypeVar('T')
ScalarOrNDArray: TypeAlias = T | npt.NDArray[T]
TimeScalarOrNDArray: TypeAlias = Time | npt.NDArray[float]
ListOrNDArray: TypeAlias = List[T] | npt.NDArray[T]

ZeroTime: Final[timedelta] = timedelta()
Day: Final[timedelta] = timedelta(days=1)

# Convenient type alias for Interval
Interval: TypeAlias = npt.NDArray[int]


class Instantiable(Generic[T]):
    """
    Something that calls an instantiable function to defer creation until invoked.
    """
    def __init__(self, func: Callable[[], T]):
        self.func = func

    def __call__(self) -> T:
        return self.func()


class MinMax(Enum):
    '''
    Enum typically to be used as dictionary keys when we have a dictionary
    that has both a min value and a max value key: that way we do not have
    to repeat the magic strings 'min' and 'max' in the code.

    Furthermore, it will always be the case that MIN < MAX, in case that is needed.
    '''
    MIN = auto()
    MAX = auto()