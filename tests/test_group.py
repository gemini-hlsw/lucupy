# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import pytest

from .fixtures import observation, observation_group, scheduling_group


@pytest.mark.usefixtures('observation_group')
def test_unique_observation_group_id(observation_group):
    """
    Test a unique ID for an observation group.
    """
    assert observation_group.unique_id.id == observation_group.id.id


@pytest.mark.usefixtures('scheduling_group')
def test_unique_scheduling_group_id(scheduling_group):
    """
    Test a unique ID for a scheduling group.
    """
    assert scheduling_group.unique_id.id == f'{scheduling_group.program_id.id}:{scheduling_group.id.id}'


@pytest.mark.usefixtures('scheduling_group', 'observation_group')
def test_subgroup_unique_ids(scheduling_group, observation_group):
    """
    Test the subgroup_unique_ids method.
    """
    assert (scheduling_group.subgroup_unique_ids()
            == frozenset({scheduling_group.unique_id, observation_group.unique_id}))


@pytest.mark.usefixtures('scheduling_group', 'observation_group')
def test_subgroup_ids(scheduling_group, observation_group):
    """
    Test the subgroup_ids method.
    """
    assert scheduling_group.subgroup_ids() == frozenset({scheduling_group.id, observation_group.id})


@pytest.mark.usefixtures('observation_group', 'observation')
def test_observation_ids(observation_group, observation):
    """
    Test conversion to / from observation id and observation group unique id.
    """
    assert observation_group.to_observation_id == observation.id
    assert observation.to_unique_group_id == observation_group.unique_id


@pytest.mark.usefixtures('scheduling_group')
def test_schedule_group_to_obsid_raises_exception(scheduling_group):
    with pytest.raises(TypeError) as exc_info:
        no = scheduling_group.to_observation_id
    assert str(exc_info.value) == 'Cannot get an ObservationID from a scheduling group.'
