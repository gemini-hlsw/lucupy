# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from copy import deepcopy
from datetime import datetime, timedelta

from lucupy.minimodel import (ROOT_GROUP_ID, AndGroup, AndOption, Band,
                              CloudCover, Conditions, Constraints,
                              ElevationType, ImageQuality, Magnitude,
                              MagnitudeBands, Observation, ObservationClass,
                              ObservationStatus, Priority, Program,
                              ProgramMode, ProgramTypes, Semester,
                              SemesterHalf, SetupTimeType, SiderealTarget,
                              Site, SkyBackground, TargetType,
                              TimeAccountingCode, TimeAllocation, TimingWindow,
                              WaterVapor)


def test_immutable_deepcopy():
    m1 = Magnitude(band=MagnitudeBands.R,
                   value=1.)
    m2 = Magnitude(band=MagnitudeBands.B,
                   value=2.)

    t = SiderealTarget(name='t',
                       magnitudes=frozenset({m1, m2}),
                       type=TargetType.BASE,
                       ra=0.,
                       dec=0.,
                       pm_ra=1.,
                       pm_dec=-1.,
                       epoch=2000.)

    conditions = Conditions(cc=CloudCover.CC50,
                            iq=ImageQuality.IQ20,
                            sb=SkyBackground.SB50,
                            wv=WaterVapor.WVANY)

    tw = TimingWindow(start=datetime(year=2022, month=12, day=21, hour=0, minute=5, second=30),
                      duration=TimingWindow.INFINITE_DURATION,
                      repeat=TimingWindow.NON_REPEATING,
                      period=TimingWindow.NO_PERIOD)

    c = Constraints(conditions=conditions,
                    elevation_type=ElevationType.AIRMASS,
                    elevation_min=Constraints.DEFAULT_AIRMASS_ELEVATION_MIN,
                    elevation_max=Constraints.DEFAULT_AIRMASS_ELEVATION_MAX,
                    timing_windows=[tw])

    o = Observation(id='o1',
                    internal_id='3829381',
                    order=0,
                    title='Observation 1',
                    site=Site.GN,
                    status=ObservationStatus.READY,
                    active=True,
                    priority=Priority.MEDIUM,
                    setuptime_type=SetupTimeType.REACQUISITION,
                    acq_overhead=timedelta(minutes=10),
                    obs_class=ObservationClass.SCIENCE,
                    targets=[t],
                    guiding={},
                    sequence=[],
                    constraints=c,
                    belongs_to='p1')

    gp = AndGroup(id='g1',
                  program_id='p1',
                  group_name='Group 1',
                  number_to_observe=1,
                  delay_min=timedelta(),
                  delay_max=timedelta(),
                  children=o,
                  group_option=AndOption.ANYORDER)

    root = AndGroup(id=ROOT_GROUP_ID,
                    program_id='p1',
                    group_name=ROOT_GROUP_ID,
                    number_to_observe=1,
                    delay_min=timedelta(),
                    delay_max=timedelta(),
                    children=[gp],
                    group_option=AndOption.ANYORDER)

    s = Semester(year=2022,
                 half=SemesterHalf.B)

    ta = TimeAllocation(category=TimeAccountingCode.KR,
                        program_awarded=timedelta(hours=2),
                        partner_awarded=timedelta(minutes=30),
                        program_used=timedelta(minutes=30),
                        partner_used=timedelta())

    p = Program(id='p1',
                internal_id='223e2332',
                semester=s,
                band=Band.BAND2,
                thesis=False,
                mode=ProgramMode.QUEUE,
                type=ProgramTypes.Q,
                start=datetime.now(),
                end=datetime.now(),
                allocated_time=frozenset({ta}),
                root_group=root)

    p2 = deepcopy(p)

    # Program should not be the same.
    assert p is not p2

    # Semester should be the same.
    assert p.semester is p2.semester

    # Time Allocation should not be the same.
    assert p.allocated_time is not p2.allocated_time

    # Root group should not be the same.
    root2 = p2.root_group
    assert root is not root2

    # Child group should not be the same.
    gp2 = root2.children[0]
    assert gp is not gp2

    # Observation should not be the same.
    o2 = gp2.children
    assert o is not o2

    # Constraints should be the same. This will implicitly test timing windows as well.
    assert o.constraints is o2.constraints

    # Targets should be the same. This will implicitly test magnitudes as well.
    assert o.targets[0] is o2.targets[0]
