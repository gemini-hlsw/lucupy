# Copyright (c) 2016-2023 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import sys
from datetime import datetime
from typing import Tuple


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


def sixty(dd: float) -> Tuple[float, float, float]:
    """Sixty

    Args:
        dd (float): Days

    Returns:
        Tuple[float, float, float]: Degrees, minutes and seconds
    """
    is_positive = dd >= 0
    l_dd = abs(dd)
    minutes, seconds = divmod(l_dd * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    if degrees > 0.:
        degrees = degrees if is_positive else -degrees
    elif minutes > 0.:
        minutes = minutes if is_positive else -minutes
    else:
        seconds = seconds if is_positive else -seconds
    return degrees, minutes, seconds


def dec2sex(d: float,
            p: int = 3,
            cutsec: bool = False,
            hour: bool = False,
            tohour: bool = False,
            sep: str = ':',
            leadzero: int = 0,
            round_min: bool = False) -> str:
    """Convert decimal degrees/hours to a formatted sexigesimal string.

    Args:
        d: Input in degrees
        p: Digits for seconds
        cutsec: Cut seconds, just display, e.g. DD:MM
        hour: d is decimal hours, so must be <=24
        tohour: Convert from degress to hours (divide by 15.)
        sep: Separator string
        leadzero: If >0 display leading 0's, e.g. -05:25. The value is the number of digits for the DD or HR field.
        round_min: When cutsec, round to the nearest minute rather than truncate
    Returns:
        str: That modify string
    """
    l_d = float(d)
    sign = ''
    maxdg = 360.

    if tohour:
        l_d /= 15.0
        hour = True

    if hour and (abs(l_d) > 24.):
        print('Input in hours must be less than or equal to 24.0.')
        sys.exit(1)

    if hour:
        maxdg = 24.0

    n = 2 if p == 0 else 3
    secstr = '{:0' + '{:1d}'.format(n + p) + '.' + '{:1d}'.format(p) + 'f}'

    six = sixty(l_d)

    dg = abs(int(six[0]))
    if six[0] < 0:
        sign = '-'

    if leadzero > 0:
        sldg = '0' + str(leadzero)
    else:
        sldg = str(len(str(dg)))

    mn = abs(int(six[1]))
    if six[1] < 0:
        sign = '-'

    sc = float(secstr.format(abs(six[2])))
    if six[2] < 0.0:
        sign = '-'

    if sc >= 60.0:
        sc -= 60.0
        mn += 1

    if cutsec:
        if round_min and sc >= 30.:
            # Round to the nearest minute, otherwise truncate
            mn += 1
        sc = 0.0

    if mn >= 60:
        mn -= 60
        dg += 1

    if dg >= int(maxdg):
        dg -= int(maxdg)

    if cutsec and sc == 0.0:
        fmt = '{:1s}{:' + sldg + 'd}' + sep + '{:02d}'
        s = fmt.format(sign, dg, mn)
    else:
        fmt = '{:1s}{:' + sldg + 'd}' + sep + '{:02d}' + sep + secstr
        s = fmt.format(sign, dg, mn, sc)

    return s.strip()
