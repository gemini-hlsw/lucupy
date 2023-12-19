# Copyright (c) 2016-2023 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from datetime import datetime, timedelta
from math import ceil
from typing import Tuple


def hms2dec(hours: float, minutes: float, seconds: float, to_degree: bool = False) -> float:
    """
    Convert hours, minutes, and seconds to decimal.

    Args:
        hours (float): the number of hours
        minutes (float): the number of minutes
        seconds (float): the number of seconds
        to_degree (bool, optional): option to convert to degree, with default False

    Returns:
        float: the decimal equivalent
    """
    factor = 15.0 if to_degree else 1.0
    sign = -1.0 if hours < 0 else 1.0
    return sign * factor * (abs(hours) + minutes / 60.0 + seconds / 3600.0)


def sex2dec(stime: str,
            to_degree: bool = False,
            sep: str = ':') -> float:
    """Sexadecimal to decimal

    Args:
        stime (str): A string of format "HR:MIN:SEC"
        to_degree (bool, optional): Option to convert to degree. Defaults to False.
        sep (str, optional): Separator. Defaults to ':'.

    Raises:
        ValueError: Wrong format for not following the separator convention.

    Returns:
        float: The decimal equivalent
    """
    try:
        hours, minutes, seconds = map(float, stime.split(sep))
        return hms2dec(hours, minutes, seconds, to_degree)
    except ValueError:
        raise ValueError(f'Input must be in the format "HR{sep}MIN{sep}SEC"')


def dt2dec(dt: datetime,
           to_degree: bool = False) -> float:

    """Datetime to decimals

    Returns:
        float: The decimal equivalent
    """
    return hms2dec(dt.hour, dt.minute, dt.second, to_degree)


def days2dms(days: float) -> Tuple[float, float, float]:
    """Convert days into degrees, minutes, and seconds of arc.

    Args:
        days (float): Days

    Returns:
        Tuple[float, float, float]: Degrees, minutes, and seconds
    """
    is_positive = days >= 0
    l_dd = abs(days)
    total_seconds = l_dd * 3600.0
    degrees, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return (degrees if is_positive else -degrees,
            minutes if is_positive else -minutes,
            seconds if is_positive else -seconds)


def dec2sex(
    degrees: float,
    precision: int = 3,
    cut_seconds: bool = False,
    input_is_hours: bool = False,
    to_hours: bool = False,
    separator: str = ':',
    leading_zeros: int = 0,
    round_minutes: bool = False,
) -> str:
    """Convert decimal degrees/hours to a formatted sexigesimal string.

    Args:
        degrees (float): Input in degrees
        precision (int, optional): Digits for seconds. Defaults to 3.
        cut_seconds (bool, optional): Cut seconds, just display, e.g. DD:MM. Defaults to False.
        input_is_hours (bool, optional): If True, input is in decimal hours, must be <=24. Defaults to False.
        to_hours (bool, optional): Convert from degrees to hours (divide by 15.). Defaults to False.
        separator (str, optional): Separator string. Defaults to ':'.
        leading_zeros (int, optional): If > 0, display leading 0's. Defaults to 0.
        round_minutes (bool, optional): When cut_seconds, round to the nearest minute rather than truncate.
            Defaults to False.

    Returns:
        str: The modified string
    """
    if to_hours:
        degrees /= 15.0
        input_is_hours = True

    if input_is_hours and abs(degrees) > 24.0:
        raise ValueError(f'Input in hours must be less than or equal to 24: {abs(degrees)}')

    max_degrees = 360.0 if not input_is_hours else 24.0

    # Determine the number of decimal places for seconds
    seconds_format = f'{{:0.{precision}f}}'

    # Convert the degrees to degrees, minutes, and seconds
    degrees, minutes, seconds = days2dms(degrees if not input_is_hours else degrees * 15)

    # Handle negative values
    sign = '-' if degrees < 0 else ''
    degrees = abs(int(degrees))
    minutes = abs(int(minutes))
    seconds = float(seconds_format.format(abs(seconds)))

    # Handle rounding or truncating seconds
    if cut_seconds:
        if round_minutes and seconds >= 30.0:
            minutes += 1
        seconds = 0.0

    # Handle minutes and hours overflow
    if minutes >= 60:
        minutes -= 60
        degrees += 1

    if degrees >= max_degrees:
        degrees -= max_degrees

    # Format the result string
    degrees_format = f'{{:0{leading_zeros}d}}'
    result_format = f'{sign}{degrees_format}{separator}{minutes:02d}'

    if not cut_seconds or seconds != 0.0:
        result_format += f'{separator}{seconds}'

    return result_format


def time2slots(time_slot_length: timedelta, time_quantity: timedelta) -> int:
    """
    Convert time_quantity into the number of time slots given the time slot length.
    This takes the ceil, so it ensures that the time_quantity supplied fits into
    the number of time slots returned.

    Notes:
        The units in the actual time_quantities are unimportant: the return type is without unit.

    Args:
        time_slot_length: the length of a time slot as a timedelta
        time_quantity: the amount of time as a timedelta that we want to know in terms of time slots

    Returns:
        the ceiling of the number of time slots required to accommodate the time quantity (unitless)
    """
    return ceil(time_quantity / time_slot_length)
