# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from datetime import date

import numpy as np

from lucupy.minimodel import (CloudCover, Conditions, ImageQuality, Semester,
                              SemesterHalf, SkyBackground, WaterVapor)


def test_most_restrictive_conditions1():
    """
    Test an empty set of Conditions to make sure that it returns the least
    restrictive conditions.
    """
    mrc = Conditions.most_restrictive_conditions(())
    c = Conditions(cc=CloudCover(1.0), iq=ImageQuality(1.0), sb=SkyBackground(1.0), wv=WaterVapor(1.0))
    assert mrc == c


def test_most_restrictive_conditions2():
    """
    Test a mixture of various conditions.
    """
    cc1 = Conditions(cc=np.array([CloudCover(0.7), CloudCover(0.8)]),
                     iq=np.array([ImageQuality(0.85), ImageQuality(1.0)]),
                     sb=np.array([SkyBackground(0.5), SkyBackground(1.0)]),
                     wv=np.array([WaterVapor(0.8), WaterVapor(0.8)]))
    cc2 = Conditions(cc=CloudCover(1.0),
                     iq=ImageQuality(1.0),
                     sb=SkyBackground(0.8),
                     wv=WaterVapor(0.2))

    mrc = Conditions.most_restrictive_conditions((cc1, cc2))
    exp = Conditions(cc=CloudCover(0.7), iq=ImageQuality(0.85), sb=SkyBackground(0.5), wv=WaterVapor(0.2))
    assert mrc == exp


# def test_most_restrictive_conditions3():
#     """
#     np.asarray causes problems due to 0-dim array.
#     """
#     cc1 = Conditions(cc=np.asarray(CloudCover(1.0)),
#                      iq=np.asarray(ImageQuality(1.0)),
#                      sb=np.asarray(SkyBackground(0.8)),
#                      wv=np.asarray(WaterVapor(0.2)))
#     cc2 = Conditions(cc=np.array([CloudCover(0.7), CloudCover(0.8)]),
#                      iq=np.array([ImageQuality(0.85), ImageQuality(1.0)]),
#                      sb=np.array([SkyBackground(0.5), SkyBackground(1.0)]),
#                      wv=np.array([WaterVapor(0.8), WaterVapor(0.8)]))
#
#     mrc = Conditions.most_restrictive_conditions((cc1, cc2))
#     exp = Conditions(cc=CloudCover(0.7), iq=ImageQuality(0.85), sb=SkyBackground(0.5), wv=WaterVapor(0.2))
#     assert mrc == exp


def test_most_restrictive_conditions4():
    cc1 = Conditions(cc=CloudCover(0.7), iq=ImageQuality(0.7), sb=SkyBackground(1.0), wv=WaterVapor(0.8))
    mrc = Conditions.most_restrictive_conditions((cc1,))
    assert mrc == cc1


def test_semesterhalf_a_lookup():
    d = date(2022, 12, 31)
    semester = Semester.find_semester_from_date(d)
    assert semester.year == 2022
    assert semester.half == SemesterHalf.B


def test_semesterhalf_a():
    s = Semester(2022, SemesterHalf.A)
    assert s.start_date() == date(2022, 2, 1)
    assert s.end_date() == date(2022, 7, 31)


def test_semesterhalf_b():
    s = Semester(2022, SemesterHalf.B)
    assert s.start_date() == date(2022, 8, 1)
    assert s.end_date() == date(2023, 1, 31)


def test_semesterhalf_b_lookup2():
    d = date(2022, 8, 1)
    semester = Semester.find_semester_from_date(d)
    assert semester.year == 2022
    assert semester.half == SemesterHalf.B


def test_semesterhalf_b_lookup1():
    d = date(2022, 1, 31)
    semester = Semester.find_semester_from_date(d)
    assert semester.year == 2021
    assert semester.half == SemesterHalf.B
