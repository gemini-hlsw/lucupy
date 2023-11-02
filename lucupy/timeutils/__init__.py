# Copyright (c) 2016-2023 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from datetime import datetime


def sex2dec(stime: str,
            todegree: bool = False,
            sep: str = ':') -> float:
    """"Sexadecimal to decimal

    Args:
        stime (str): A string of format "HR:MIN:SEC
        todegree (bool, optional): Option to convert to degree. Defaults to False.
        sep (str, optional): Separator. Defaults to ':'.

    Raises:
        ValueError: Wrong format for not following the separator convention.

    Returns:
        float: The decimal equivalent
    """
    l_stime = str(stime).replace("+", "")
    if sep not in l_stime:
        raise ValueError(f'Separator {sep} not found in {stime}. Input must be in the format "HR<sep>MIN<sep>SEC"')

    f = 1.0
    if todegree:
        f = 15.0

    result = 0.0
    exp = 0
    sign = 1.
    for val in l_stime.split(sep):
        x = float(val)
        if x < 0.0:
            sign = -1.
        result += abs(x) / 60. ** exp
        exp += 1
    return sign * f * result


def dtsex2dec(dt: datetime,
              todegree: bool = False) -> float:

    """Datetime to decimals

    Returns:
        float: The decimal equivalent
    """
    f = 1.0
    if todegree:
        f = 15.0

    sign = 1.
    if dt.hour < 0:
        sign = -1.
    return sign * f * (abs(dt.hour) + dt.minute / 60. + dt.second / 3600.)
