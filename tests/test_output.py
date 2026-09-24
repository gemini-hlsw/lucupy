# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import io
import unittest.mock
from datetime import datetime

from lucupy.minimodel import (GROUP_NONE_ID, ROOT_GROUP_ID, AndOption, Group, GroupID, Observation,
                              ObservationClass, ObservationID, ObservationStatus, Program,
                              ProgramID)


@unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
def assert_stdout(p, expected_output, mock_stdout):
    p.show()
    assert mock_stdout.getvalue() == expected_output


def test_print_program():
    """
    Test the print_program function.
    """
    program_id = ProgramID('test_program')

    o = Observation(
        id=ObservationID('test_observation'),
        internal_id='acc39a30-97a8-42de-98a6-5e77cc95d3ec',
        order=0,
        title='GMOSN-1',
        site=None,
        status=ObservationStatus.READY,
        active=True,
        priority=None,
        setuptime_type=None,
        acq_overhead=None,
        obs_class=ObservationClass.SCIENCE,
        targets=None,
        guiding=None,
        sequence=[],
        constraints=None,
        belongs_to=program_id,
        too_type=None
    )

    # Create the trivial AND group containing the gnirs1 observation.
    g1 = Group(
        id=GroupID('test_group'),
        program_id=program_id,
        group_name='test',
        parent_id=ROOT_GROUP_ID,
        previous_id=GROUP_NONE_ID,
        next_id=GROUP_NONE_ID,
        number_to_observe=1,
        number_observed=0,
        delay_min=None,
        delay_max=None,
        active=True,
        children=o,
        group_option=AndOption.ANYORDER
    )

    g = Group(id=ROOT_GROUP_ID,
                 program_id=program_id,
                 group_name=ROOT_GROUP_ID.id,
                 parent_id=GROUP_NONE_ID,
                 previous_id=GROUP_NONE_ID,
                 next_id=GROUP_NONE_ID,
                 number_to_observe=1,
                 number_observed=0,
                 delay_min=None,
                 delay_max=None,
                 active=True,
                 children=[g1],
                 group_option=AndOption.ANYORDER,
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
        used_time=None,
        root_group=g,
        too_type=None,
    )

    expected_output = (
        'Program: test_program\n'
        f'----- Group: {ROOT_GROUP_ID.id}, unique_id=test_program:{ROOT_GROUP_ID.id}, parent={GROUP_NONE_ID.id}, '
        f'previous={GROUP_NONE_ID.id}, next={GROUP_NONE_ID.id}, active=True, ToO=None '
        f'({AndOption.ANYORDER}, num_children=1, num_observe=1, num_observed=0)\n'
        f'---------- Group: test_group, unique_id=test_program:test_group, parent={ROOT_GROUP_ID.id}, '
        f'previous={GROUP_NONE_ID.id}, next={GROUP_NONE_ID.id}, active=True, ToO=None '
        '(Observation Group, num_children=1, num_observe=1, num_observed=0)\n'
        f'--------------- Observation: test_observation {o.status.name} None {o.obs_class.name} None\n'
    )
    assert_stdout(p, expected_output)
