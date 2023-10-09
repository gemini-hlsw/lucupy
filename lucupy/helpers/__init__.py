# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import bisect
from collections.abc import Iterable
from datetime import timedelta
from enum import Enum
from typing import List, Optional, Type

import astropy.units as u
import numpy as np
import numpy.typing as npt
from astropy.time import Time, TimeDelta


def is_contiguous(iterable: Iterable) -> bool:
    """
    Determine if a sortable iterable contains contiguous elements.
    Args:
        iterable: an iterable collection that can be sorted

    Returns:
        True if the elements are contiguous, and False otherwise
    """
    s = sorted(iterable)
    diffs = np.diff(s)
    return np.all(diffs == 1)


def flatten(lst):  # type: ignore
    """Flattens any iterable, no matter how irregular.
       Deliberately left untyped to allow for maximum type usage.

    Example:
        flatten([1, 2, [3, 4, 5], [[6, 7], 8, [9, 10]]])

    Args:
        lst: n-dimensional array

    Yields:
        Value of the iterable.
    """
    for el in lst:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el


def round_minute(time: Time, up: bool = False) -> Time:
    """Round a time down (truncate) or up to the nearest minute time: an astropy.Time

    Args:
        time: times value(s) to round down/up
        up: bool indicating whether to round up

    Returns:
        Round up/down value(s) on Astropy Time object
    """
    t = time.copy()
    t.format = 'iso'
    t.out_subfmt = 'date_hm'
    if up:
        sec = t.strftime('%S').astype(int)
        idx = np.where(sec > 0)
        t[idx] += 1.0 * u.min
    return Time(t.iso, format='iso', scale='utc')


def str_to_bool(s: Optional[str]) -> bool:
    """Conversion from string to bolean

    Arg:
        s: parameter to convert

    Returns:
        true if and only if s is defined and some variant capitalization of 'yes' or 'true'.
    """
    return s is not None and s.strip().upper() in ['YES', 'TRUE']


# A dict of signs for conversion.
SIGNS = {'': 1, '+': 1, '-': -1}


def dmsstr2deg(s: str) -> float:
    """Degrees, minutes, seconds (in string form) to decimal degrees

    Args:
        s: string to convert

    Raises:
        ValueError: wrong format

    Returns:
        float: value in decimal degrees

    """
    if not s:
        raise ValueError(f'Illegal DMS string: {s}')

    sign = '+'
    if s[0] in SIGNS:
        sign = s[0]
        s = s[1:]

    result = s.split(':')
    if len(result) != 3:
        raise ValueError(f'Illegal DMS string: {s}')
    return dms2deg(int(result[0]), int(result[1]), float(result[2]), sign)


def dms2deg(d: int, m: int, s: float, sign: str) -> float:
    """Degrees, minutes, seconds to decimal degrees

    Args:
        d (int): Degree
        m (int): Minute
        s (float): Seconds
        sign (str): Mathematical sign

    Raises:
        ValueError: If signs is not in the SIGN dictionary

    Returns:
        float: Decimal degrees value
    """
    if sign not in SIGNS:
        raise ValueError(f'Illegal sign "{sign}" in DMS: {sign}{d}:{m}:{s}')
    dec = SIGNS[sign] * (d + m / 60.0 + s / 3600.0)
    return dec if dec < 180 else -(360 - dec)


def dms2rad(d: int, m: int, s: float, sign: str) -> float:
    """Degrees, minutes, seconds to radians

    Args:
        d (int): Degree
        m (int): Minute
        s (float): Seconds
        sign (str): Mathematical sign

    Raises:
        ValueError: If signs is not in the SIGN dictionary

    Returns:
        float: Radian value
    """
    return dms2deg(d, m, s, sign) * np.pi / 180.0


def hmsstr2deg(s: str) -> float:
    """HH:mm:ss in string to degrees

    Args:
        s (str): String to be transform

    Raises:
        ValueError: Wrong format

    Returns:
        float: Value in degrees
    """
    if not s:
        raise ValueError(f'Illegal HMS string: {s}')

    result = s.split(':')
    if len(result) != 3:
        raise ValueError(f'Illegal HMS string: {s}')

    return hms2deg(int(result[0]), int(result[1]), float(result[2]))


def hms2deg(h: int, m: int, s: float) -> float:
    """HH:mm:ss to degrees

    Args:
        h (int): Hour
        m (int): Minute
        s (float): Second

    Returns:
        float: Value in degrees
    """
    return h + m / 60.0 + s / 3600.0


def hms2rad(h: int, m: int, s: float) -> float:
    """HH:mm:ss to radians

    Args:
        h (int): Hour
        m (int): Minute
        s (float): Second

    Returns:
        float: Value in degrees
    """
    return hms2deg(h, m, s) * np.pi / 12.


def angular_distance(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
    """Calculate the angular distance between two points on the sky.
    based on
    https://github.com/gemini-hlsw/lucuma-core/blob/master/modules/core/shared/src/main/scala/lucuma/core/math/Coordinates.scala#L52

    Args:
        ra1 (float): Right Ascension for point 1
        dec1 (float): Declination for point 1
        ra2 (float): Right Ascension for point 2
        dec2 (float): Declination for point 2

    Returns:
        float: Angular Distance
    """
    phi_1 = dec1
    phi_2 = dec2
    delta_phi = dec2 - dec1
    delta_lambda = ra2 - ra1
    a = np.sin(delta_phi / 2) ** 2 + np.cos(phi_1) * np.cos(phi_2) * np.sin(delta_lambda / 2) ** 2
    return 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def lerp(first_value: float, last_value: float, n: int) -> npt.NDArray[float]:
    """
    Perform linear interpolation for n points between start_value and end_value.

    Args:
        first_value: a float value from which to start
        last_value: a float value at which to end
        n: the number of points to interpolate over

    Returns:
        A numpy array of length n that linearly interpolates exclusively between start_value and end_value.
    """
    # Create the linspace array. In order to properly interpolate, we have to add 2 to n and then cut off the first
    # and last values, which will be first_value and last_value.
    return np.linspace(first_value, last_value, n + 2)[1:-1]


def lerp_enum(enum_class: Type[Enum], first_value: float, last_value: float, n: int) -> npt.NDArray[float]:
    """
    Given an Enum of float, a first_value, a last_value, and a number of slots, interpolate over the Enum
    to create a numpy array of slots.

    Args:
        enum_class: an Enum with float values
        first_value: a value in the Enum
        last_value: a value in the Enum
        n: the number of slots to interpolate over

    Returns:
        A numpy array of length n that linearly interpolates exclusively between first_value and last_value only
        containing values from enum_class.
    """
    # Create the linspace array. In order to properly interpolate, we have to add 2 to n and then cut off the first
    # and last values, which will be first_value and last_value.
    interp_values = np.linspace(first_value, last_value, n + 2)[1:-1]

    # Sort the Enum values.
    sorted_values = sorted(o.value for o in enum_class)

    # Interpolate over the Enum.
    if first_value <= last_value:
        result = [sorted_values[bisect.bisect_left(sorted_values, x)] for x in interp_values]
    else:
        result = [sorted_values[bisect.bisect_right(sorted_values, x)] for x in interp_values]
    return np.array(result)


def _lerp_circular(first_value: float, last_value: float, n: int, max_val: float) -> npt.NDArray[float]:
    """
    Perform linear interpolation for n points between first_value and last_value.
    As this is done for a circle, max_value must be specified for the maximum value (exclusive) of measurement.
    For degrees, max_val should be 360.
    For radians, max_val should be 2π.

    Args:
        first_value: a float value from which to start
        last_value: a float value at which to end
        n: the number of points to interpolate over
        max_val: the maximum value (exclusive) of the units of measurement

    Returns:
        A numpy array of length n that linearly interpolates exclusively between:
        (first_value % max_val) and (last_value % max_val)
        with values in the range [0, max_val), taking the shortest route around the circle.

        If the points are antipodal, and:
        * (first_value % max_value) < (last_value % max_value), the clockwise direction is taken.
        * (first value % max_value) > (last_value % max_value), the counter-clockwise direction is taken.
    """
    if max_val <= 0:
        raise ValueError(f'Circular linear interpolation requires positive maximum value, received: {max_val}.')

    # Normalize start and end values to the range [0, max_val).
    first_value %= max_val
    last_value %= max_val

    # Calculate distances.
    direct_clockwise_distance = (last_value - first_value) % max_val
    direct_counterclockwise_distance = (first_value - last_value) % max_val

    # Choose the direction with the shortest distance.
    if direct_clockwise_distance < direct_counterclockwise_distance:
        shortest_distance = direct_clockwise_distance
    else:
        shortest_distance = -direct_counterclockwise_distance

    # Generate the lerp.
    return (first_value + shortest_distance * lerp(0, 1, n)) % max_val


def lerp_radians(start_value: float, end_value: float, n: int) -> npt.NDArray[float]:
    """
    Perform linear interpolation for n points around a circle in radians.

    Args:
        start_value: a float value in radians from which to start
        end_value: a float value in radians at which to end
        n: the number of points to interpolate over

    Returns:
        A numpy array of length n that linearly interpolates exclusively between:
        (first_value % 2π) and (last_value % 2π)
        in radians, taking the shortest route around the circle.

        If the points are antipodal, i.e. at distance π, and:
        * (first_value % 2π) < (last_value % 2π), the clockwise direction is taken.
        * (first value % 2π) > (last_value % 2π), the counter-clockwise direction is taken.

    Raises:
        ValueError if max_val <= 0.
    """
    return _lerp_circular(start_value, end_value, n, 2 * np.pi)


def lerp_degrees(start_value: float, end_value: float, n: int) -> npt.NDArray[float]:
    """
    Perform linear interpolation for n points around a circle in degrees.

    Args:
        start_value: a float value in degrees from which to start
        end_value: a float value in degrees at which to end
        n: the number of points to interpolate over

    Returns:
        A numpy array of length n that linearly interpolates exclusively between:
        (first_value % 360) and (last_value % 360)
        in degrees, taking the shortest route around the circle.

        If the points are antipodal, i.e. at distance 180, and:
        * (first_value % 360) < (last_value % 360), the clockwise direction is taken.
        * (first value % 360) > (last_value % 360), the counter-clockwise direction is taken.
    """
    return _lerp_circular(start_value, end_value, n, 360.0)


def timedelta_astropy_to_python(time_delta: TimeDelta) -> timedelta:
    """
    Convert an AstroPy TimeDelta to a Python timedelta in seconds.

    Args:
        time_delta: an AstroPy TimeDelta

    Returns:
        the equivalent Python timedelta in seconds

    Raises:
        ValueError if TimeDelta is not a scalar.
    """
    if time_delta.ndim != 0:
        raise ValueError(f'time_slot_length contains multiple values: {len(time_delta.value)}')

    return timedelta(seconds=time_delta.to_value(u.s))


def time_delta_astropy_to_minutes(time_delta: TimeDelta) -> int:
    """
    Convert an AstroPy TimeDelta
    Args:
        time_delta: an AstroPy TimeDelta

    Returns:
        An int representing the number of minutes in the AstroPy TimeDelta.

    Raises:
        ValueError if TimeDelta is not a scalar in minutes.
    """
    if time_delta.ndim != 0:
        raise ValueError(f'time_slot_length contains multiple values: {len(time_delta.value)}')
    minutes = time_delta.to_value(u.minute)

    if int(minutes) != minutes:
        raise ValueError(f'time_slot_length is not a multiple of minutes: {minutes} minutes.')

    return int(minutes)


def first_nonzero_time(inlist: List[timedelta]) -> Optional[int]:
    """Find the index of the first nonzero timedelta in inlist
       Designed to work with the output from cumulative_seq_exec_times
       Args:
           inlist (List[timedelta]): a list of cumulative timedelta objects

       Returns:
          Optional[int]: return the index for the first non-zero, if it does
          not exist return None
    """
    for i, td in enumerate(inlist):
        if td != timedelta(0):
            return i
    return None


def standards_for_nir(exec_sci: timedelta,
                      wavelengths: Optional[List[float]] = None,
                      mode: str = 'spectroscopy') -> int:
    """
    Calculated the number of NIR standards from the length of the NIR science and the mode
    Args:
        exec_sci(timedelta): execution time for science
        wavelengths (List[float]): list of wavelengths values
        mode (str): mode for the NIR observation
    """

    # TODO: need mode or other info to distinguish imaging from spectroscopy
    if mode == 'imaging':
        time_per_standard = timedelta(hours=2.0)
    else:
        if wavelengths:
            if all(wave <= 2.5 for wave in wavelengths):
                time_per_standard = timedelta(hours=1.5)
            else:
                time_per_standard = timedelta(hours=1.0)
        else:
            raise ValueError("Wrong mode: spectroscopy expects a non-empty wavelengths list.")

    return max(1, int(exec_sci // time_per_standard))  # TODO: confirm this
