# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from dataclasses import dataclass
from datetime import date
from enum import Enum


class SemesterHalf(str, Enum):
    """Gemini typically schedules programs for two semesters per year, namely A and B.
    For other observatories, this logic might have to be substantially changed.

    Members:
        - A = 'A'
        - B = 'B'
    """
    A = 'A'
    B = 'B'

    def start_month(self) -> int:
        return 2 if self == SemesterHalf.A else 8

    def end_month(self) -> int:
        return 7 if self == SemesterHalf.A else 1


@dataclass(frozen=True, order=True)
class Semester:
    """ A semester is a period for which programs may be submitted to Gemini.

    Attributes:
        year (int): A four digit year.
        half (SemesterHalf): Two semesters during each year, indicated by the SemesterHalf.
    """
    year: int
    half: SemesterHalf

    def start_date(self) -> date:
        return date(year=self.year, month=self.half.start_month(), day=1)

    def end_date(self) -> date:
        return date(year=self.year, month=self.half.end_month(), day=31)

    def __str__(self):
        return f'{self.year}{self.half.value}'
