# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import pytest

from .fixtures import observation, observation_group, scheduling_group


@pytest.mark.usefixtures('observation_group')
def test_unique_observation_group_id(observation_group):
    """
    Test a unique ID for an observation group.
    """
    assert observation_group.unique_id() == observation_group.id


@pytest.mark.usefixtures('scheduling_group')
def test_unique_scheduling_group_id(scheduling_group):
    """
    Test a unique ID for a scheduling group.
    """
    assert scheduling_group.unique_id() == f'{scheduling_group.program_id}:{scheduling_group.id}'
