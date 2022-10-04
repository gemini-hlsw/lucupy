
- sex2dec(stime: str, todegree: bool = False, sep: str = ':') -> float:
    
    stime is a string of format "HR:MIN:SEC"
    Returns the decimal equivalent.


- dtsex2dec(dt: datetime, todegree: bool = False) -> float:

- sixty(dd: float) -> Tuple[int, int, int]:


def dec2sex(d: float, p: int = 3, cutsec: bool = False, hour: bool = False, tohour: bool = False, sep: str = ':', leadzero: int = 0, round_min: bool = False) -> str:
    Convert decimal degrees/hours to a formatted sexigesimal string.

    Parameters
    d: input in degrees
    p: digits for seconds
    cutsec: Cut seconds, just display, e.g. DD:MM
    hour: d is decimal hours, so must be <=24
    tohour: convert from degress to hours (divide by 15.)
    sep: Separator string
    leadzero: if >0 display leading 0's, e.g. -05:25. The value is the number of digits for the DD or HR field.
    round_min: when cutsec, round to the nearest minute rather than truncate