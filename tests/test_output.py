# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from datetime import datetime

from lucupy.minimodel import Program, AndGroup, Observation
from lucupy.output import print_program


def test_print_program():
    """
    Test the print_program function.
    """

    o = Observation(
        id='test',
        internal_id='acc39a30-97a8-42de-98a6-5e77cc95d3ec',
        order=0,
        title='GMOSN-1',
        site=None,
        status=None,
        active=True,
        priority=None,
        setuptime_type=None,
        acq_overhead=None,
        obs_class=None,
        targets=None,
        guiding=None,
        sequence=[],
        constraints=None,
        too_type=None
    )

    # Create the trivial AND group containing the gnirs1 observation.
    g1 = AndGroup(
        id='test',
        group_name='test',
        number_to_observe=1,
        delay_min=None,
        delay_max=None,
        children=o,
        group_option=None
    )

    g = AndGroup(id='test',
                 group_name='test',
                 number_to_observe=1,
                 delay_min=None,
                 delay_max=None,
                 children=[g1],
                 group_option=None,
                 )
    p = Program(
        id='test',
        internal_id='c396b9c9-9bdd-4eec-be83-81162090d032',
        semester=None,
        band=None,
        thesis=True,
        mode=None,
        type=None,
        start=datetime(2022, 8, 1, 0, 0) - Program.FUZZY_BOUNDARY,
        end=datetime(2023, 1, 31, 0, 0) + Program.FUZZY_BOUNDARY,
        allocated_time=None,
        root_group=g,
        too_type=None,
    )
    print_program(p)
    assert True
