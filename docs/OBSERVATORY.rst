Observatory
###########


Abstract classes
----------------

ObservatoryProperties

Observatory-specific methods that are not tied to other components or
structures, and allow computations to be implemented in one place.

- set_properties(cls) -> NoReturn:
     
- determine_standard_time(resources: FrozenSet, wavelengths: FrozenSet[float], modes: FrozenSet, cal_length: int) -> Time:

    Given the information, determine the length in hours required for calibration on a standard star.
    
- is_instrument(resource) -> bool:

    Determine if the given resource is an instrument or not.

- acquisition_time(resource, observation_mode) -> Optional[timedelta]:
    
    Given a resource, check if it is an instrument, and if so, lookup the acquisition time for the specified mode.

Gemini Specific
---------------

- with_igrins_cal(func):
  
    Decorator that add IGRINS time to an observations

- GeminiObservation
  
    A Gemini-specific extension of the Observation class.


class GeminiProperties(ObservatoryProperties):

    Implementation of ObservatoryCalculations specific to Gemini.

   