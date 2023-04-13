# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
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
    c = Conditions(cc=CloudCover.CCANY, iq=ImageQuality.IQANY, sb=SkyBackground.SBANY, wv=WaterVapor.WVANY)
    assert mrc == c


def test_most_restrictive_conditions2():
    """
    Test a mixture of various conditions.
    """
    cc1 = Conditions(cc=np.array([CloudCover.CC70, CloudCover.CC80]),
                     iq=np.array([ImageQuality.IQ85, ImageQuality.IQANY]),
                     sb=np.array([SkyBackground.SB50, SkyBackground.SBANY]),
                     wv=np.array([WaterVapor.WV80, WaterVapor.WV80]))
    cc2 = Conditions(cc=CloudCover.CCANY,
                     iq=ImageQuality.IQANY,
                     sb=SkyBackground.SB80,
                     wv=WaterVapor.WV20)

    mrc = Conditions.most_restrictive_conditions((cc1, cc2))
    exp = Conditions(cc=CloudCover.CC70, iq=ImageQuality.IQ85, sb=SkyBackground.SB50, wv=WaterVapor.WV20)
    assert mrc == exp


# def test_most_restrictive_conditions3():
#     """
#     np.asarray causes problems due to 0-dim array.
#     """
#     cc1 = Conditions(cc=np.asarray(CloudCover.CCANY),
#                      iq=np.asarray(ImageQuality.IQANY),
#                      sb=np.asarray(SkyBackground.SB80),
#                      wv=np.asarray(WaterVapor.WV20))
#     cc2 = Conditions(cc=np.array([CloudCover.CC70, CloudCover.CC80]),
#                      iq=np.array([ImageQuality.IQ85, ImageQuality.IQANY]),
#                      sb=np.array([SkyBackground.SB50, SkyBackground.SBANY]),
#                      wv=np.array([WaterVapor.WV80, WaterVapor.WV80]))
#
#     mrc = Conditions.most_restrictive_conditions((cc1, cc2))
#     exp = Conditions(cc=CloudCover.CC70, iq=ImageQuality.IQ85, sb=SkyBackground.SB50, wv=WaterVapor.WV20)
#     assert mrc == exp


def test_most_restrictive_conditions4():
    cc1 = Conditions(cc=CloudCover.CC70, iq=ImageQuality.IQ70, sb=SkyBackground.SBANY, wv=WaterVapor.WV80)
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
