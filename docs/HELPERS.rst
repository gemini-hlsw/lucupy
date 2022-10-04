Helpers
-------

- flatten(lst):

    Flattens any iterable, no matter how irregular.
    Example: flatten([1, 2, [3, 4, 5], [[6, 7], 8, [9, 10]]])

- round_minute(time: Time, up: bool = False) -> Time:
    
    Round a time down (truncate) or up to the nearest minute
    time: an astropy.Time
    up: bool indicating whether to round up

- str_to_bool(s: Optional[str]) -> bool:
  
    Returns true if and only if s is defined and some variant capitalization of 'yes' or 'true'.

- dmsstr2deg(s: str) -> float:
    
    Degrees, minutes, seconds (in string form) to decimal degrees

- dms2deg(d: int, m: int, s: float, sign: str) -> float:

    Degrees, minutes, seconds to decimal degrees
  
- dms2rad(d: int, m: int, s: float, sign: str) -> float:
  
    Degrees, minutes, seconds to radians

- hmsstr2deg(s: str) -> float:
  
    HH:mm:ss in string to degrees

- hms2deg(h: int, m: int, s: float) -> float:
    
    HH:mm:ss in string to degrees

- hms2rad(h: int, m: int, s: float) -> float:
    
    HH:mm:ss in string to radians

- angular_distance(ra1: float, dec1: float, ra2: float, dec2: float) -> float:

    Calculate the angular distance between two points on the sky.
    based on
    https://github.com/gemini-hlsw/lucuma-core/blob/master/modules/core/shared/src/main/scala/lucuma/core/math/Coordinates.scala#L52
   

- mask_to_barcode(mask: str, inst: Optional[str]) -> str:
   
    Convert a mask string to a barcode string.


- barcode_to_mask(barcode: str, rootname: Optional[str]) -> str:
  
    Convert a barcode string to a mask string.