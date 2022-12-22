# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from datetime import datetime, timedelta

from lucupy.minimodel import (AndGroup, AndOption, Band, CloudCover, Conditions, Constraints, ElevationType, ImageQuality, Magnitude, MagnitudeBands, Observation, ObservationClass, ObservationStatus, Priority, Program, ProgramMode, ProgramTypes, ROOT_GROUP_ID, SetupTimeType, Semester, SemesterHalf, SiderealTarget, Site, SkyBackground, TargetType, TimeAccountingCode, TimeAllocation, TimingWindow, WaterVapor)


def test_deepcopy():
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
                    constraints=c)

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