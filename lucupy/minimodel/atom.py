# Copyright (c) 2016-2023 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from dataclasses import dataclass, field
from datetime import timedelta

from .observationmode import ObservationMode
from .qastate import QAState
from .resource import Resources
from .wavelength import Wavelengths


@dataclass
class Atom:
    """
    Atom information, where an atom is the smallest schedulable set of steps
    such that useful science can be obtained from performing them.
    Wavelengths must be specified in microns.

    Attributes:

        id (int): GPP atom `id`. In other case is given by the Provider
        exec_time (timedelta): Total planned time of execution.
        prog_time (timedelta): Planned program time.
        part_time (timedelta): Planned partner time.
        program_used (timedelta): Used (charged) program time.
        partner_used (timedelta): Used (charged) partner time.
        observed (bool): True if the STATUS is already observed.
        qa_state (QAState):
        guide_state (bool): True if a state exists.
        resources (Resources): Resources needed (Instrument, FPU, etc).
        wavelengths (Wavelengths): Set of wavelengths.

    """
    id: int
    exec_time: timedelta = field(hash=False, compare=False)
    prog_time: timedelta = field(hash=False, compare=False)
    part_time: timedelta = field(hash=False, compare=False)
    program_used: timedelta = field(hash=False, compare=False)
    partner_used: timedelta = field(hash=False, compare=False)
    observed: bool
    qa_state: QAState
    guide_state: bool
    resources: Resources
    wavelengths: Wavelengths
    obs_mode: ObservationMode
