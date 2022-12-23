# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from dataclasses import dataclass, field
from datetime import timedelta
from typing import FrozenSet

from .qastate import QAState
from .resource import Resource


@dataclass
class Atom:
    """
    Atom information, where an atom is the smallest schedulable set of steps
    such that useful science can be obtained from performing them.
    Wavelengths must be specified in microns.

    Attributes:

        id (int): GPP atom `id`. In other case is given by the Provider
        exec_time (timedelta): Total time of execution.
        prog_time (timedelta): Program time.
        part_time (timedelta): Partner time.
        observed (bool): True if the STATUS is already observed.
        qa_state (QAState):
        guide_state (bool): True if a state exists.
        resources (FrozenSet[Resource]): Resources needed (Instrument, FPU, etc).
        wavelengths (FrozenSet[float]): Set of wavelengths.

    """
    id: int
    exec_time: timedelta = field(hash=False, compare=False)
    prog_time: timedelta = field(hash=False, compare=False)
    part_time: timedelta = field(hash=False, compare=False)
    observed: bool
    qa_state: QAState
    guide_state: bool
    resources: FrozenSet[Resource]
    wavelengths: FrozenSet[float]
