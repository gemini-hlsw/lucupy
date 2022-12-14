# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import io
import unittest.mock
from datetime import datetime

from lucupy.minimodel import AndGroup, Observation, Program


@unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
def assert_stdout(p, expected_output, mock_stdout):
    p.show()
    assert mock_stdout.getvalue() == expected_output


def test_print_program():
    """
    Test the print_program function.
    """
    program_id = 'test_program'

    o = Observation(
        id='test_observation',
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
        id='test_group',
        program_id=program_id,
        group_name='test',
        number_to_observe=1,
        delay_min=None,
        delay_max=None,
        children=o,
        group_option=None
    )

    g = AndGroup(id='root',
                 program_id=program_id,
                 group_name='root',
                 number_to_observe=1,
                 delay_min=None,
                 delay_max=None,
                 children=[g1],
                 group_option=None,
                 )
    p = Program(
        id=program_id,
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

    expected_output = ('Program: test_program\n'
                       '----- Group: root (Scheduling Group, num_children=1)\n'
                       '---------- Group: test_group (Observation Group, num_children=1)\n'
                       '--------------- Observation: test_observation\n')
    assert_stdout(p, expected_output)
