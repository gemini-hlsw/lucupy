# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from datetime import timedelta

import astropy.units as u
import pytest
from astropy.coordinates import EarthLocation, SkyCoord
from astropy.time import Time

from lucupy.minimodel import (AndGroup, AndOption, Observation, ObservationClass, ObservationStatus, Priority,
                              SetupTimeType, Site)


@pytest.fixture
def observation():
    return Observation(
        id='GN-2018B-Q-101-1337',
        internal_id="",
        order=1,
        title='Test observation',
        site=Site.GN,
        status=ObservationStatus.READY,
        active=True,
        priority=Priority.MEDIUM,
        setuptime_type=SetupTimeType.NONE,
        acq_overhead=timedelta(),
        obs_class=ObservationClass.SCIENCE,
        targets=[],
        guiding={},
        sequence=[],
        constraints=None,
    )


@pytest.fixture
def observation_group(observation):
    return AndGroup(
        id='GN-2018B-Q-101-1337',
        program_id='GN-2018B-Q-101',
        group_name='Test observation group',
        number_to_observe=1,
        delay_min=timedelta(),
        delay_max=timedelta(),
        children=observation,
        group_option=AndOption.ANYORDER
    )


@pytest.fixture
def scheduling_group(observation_group):
    return AndGroup(
        id='10',
        program_id='GN-2018B-Q-101',
        group_name='Test scheduling group',
        number_to_observe=1,
        delay_min=timedelta(),
        delay_max=timedelta(),
        children=[observation_group],
        group_option=AndOption.ANYORDER
    )


@pytest.fixture
def midnight():
    return Time('2020-07-01 9:25:00', format='iso', scale='utc')


@pytest.fixture
def coord():
    coords = ['1:12:43.2 +31:12:43', '1 12 43.2 +31 12 43']
    return SkyCoord(coords, unit=(u.hourangle, u.deg), frame='icrs')


@pytest.fixture
def location():
    return EarthLocation.of_site('gemini_north')


@pytest.fixture
def test_time():
    return Time('2020-07-01 10:00:00.000', format='iso', scale='utc')
