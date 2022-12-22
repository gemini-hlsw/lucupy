# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Dict, List

from gelidum import freeze

from ..decorators import immutable


class SemesterHalf(str, Enum):
    """Gemini typically schedules programs for two semesters per year, namely A and B.
    For other observatories, this logic might have to be substantially changed.

    Members:
        - A = 'A'
        - B = 'B'
    """
    A = 'A'
    B = 'B'

    def start_day(self) -> int: # noqa
        return 1

    def end_day(self) -> int: # noqa
        return 31

    def start_month(self) -> int:
        return _semester_half_months[self][0]

    def end_month(self) -> int:
        return _semester_half_months[self][-1]

    @staticmethod
    def determine_half(month: int) -> 'SemesterHalf':
        """
        Given a month, return the SemesterHalf this falls in.

        Args:
            month: the month of the date

        Returns:
            The SemesterHalf in which this month occurs.
        """
        if month < 1 or month > 12:
            raise ValueError(f'Illegal month: {month}')
        for semester_half, months in _semester_half_months.items():
            if month in months:
                return semester_half
        raise ValueError(f'Month {month} cannot be found in any SemesterHalf.')


# Make a FrozenDict with values FrozenList, so the lists cannot be changed, nor can the dict.
_semester_half_months: Dict[SemesterHalf, List[int]] = freeze({
    SemesterHalf.A: [2, 3, 4, 5, 6, 7],
    SemesterHalf.B: [8, 9, 10, 11, 12, 1]
})


@immutable
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
        """
        Returns:
            The start date of the Semester.
        """
        return date(year=self.year, month=self.half.start_month(), day=self.half.start_day())

    def end_date(self) -> date:
        """
        Returns:
            The end date of the Semester.
        """
        # Check if the semester spans two years.
        if _semester_half_months[self.half][-1] < _semester_half_months[self.half][0]:
            end_year = self.year + 1
        else:
            end_year = self.year
        return date(year=end_year, month=self.half.end_month(), day=self.half.end_day())

    @staticmethod
    def find_semester_from_date(lookup_date: date) -> 'Semester':
        """
        Given a date, return the Semester in which it occurs.

        Args:
            A date object representing the date.

        Returns:
            The Semester in which this date occurs.
        """
        # Determine which semester half the date falls in.
        semester_half = SemesterHalf.determine_half(lookup_date.month)

        # If the month in the semester half is less than the first entry, it spans over a year.
        if lookup_date.month < _semester_half_months[semester_half][0]:
            semester_year = lookup_date.year - 1
        else:
            semester_year = lookup_date.year

        return Semester(year=semester_year, half=semester_half)

    def __str__(self):
        return f'{self.year}{self.half.value}'
