Minimodel
=========
The minimodel is a reduce version of the data model on the Observing Database (ODB).

Program
-------

Representation of a program.

Attributes
^^^^^^^^^^

- id
- internal_id
- semester
- band
- thesis
- mode
- type
- start
- end
- allocated_time
- root_group
- too_type
- FUZZY_BOUNDARY: The FUZZY_BOUNDARY is a constant that allows for a fuzzy boundary for a program's start and end times.

Methods
^^^^^^^

- program_awarded: 
- program_used:
- partner_awarded
- partner_used
- total_awarded
- total_used
- observations 
- get_group_ids 
- get_group


Group
-----
This is the base implementation of AND / OR Groups.
Python does not allow classes to self-reference unless in static contexts, so we make a very simple base class to self-reference from subclasses since
we need this functionality to allow for group nesting.

Attributes
^^^^^^^^^^

- id
- group_name
- number_to_observe
- delay_min
- delay_max
- children: List of either other groups or an observation.

Methods
^^^^^^^

- subgroup_ids
- sites
- required_resources
- wavelengths
- constraints
- observations
- is_observation_group
- is_scheduling_group

AndGroup
--------
The concrete implementation of an AND group. It requires an AndOption to specify how its observations should be handled,
and a previous (which should be an index into the group's children to indicate the previously observed child, or None if 
none of the children have yet been observed).

Methods
^^^^^^^

- is_and_group
- is_or_group
- exec_time
- total_used     
- instruments(self) -> FrozenSet[Resource]:


Observation
-----------
Representation of an observation.

Attributes
^^^^^^^^^^

- id: should represent the observation's ID, e.g. GN-2018B-Q-101-123.
- internal_id: internal_id is the key associated with the observation
- order: refers to the order of the observation in either its group or the program
- title
- site
- status
- active
- priority
- setuptime_type
- acq_overhead
- obs_class
- targets: should contain a complete list of all targets associated with the observation, with the base being in the first position
- guiding: is a map between guide probe resources and their targets
- sequence
- constraints: Some observations do not have constraints, e.g. GN-208A-FT-103-6.
- too_type

Methods
^^^^^^^

- base_target: Get the base target for this Observation if it has one, and None otherwise. 
- exec_time: Total execution time for the program, which is the sum across atoms and the acquisition overhead.
- total_used: Total program time used: includes program time and partner time.
- required_resources: The required resources for an observation based on the sequence's needs.
- instrument: Returns a resource that is an instrument, if one exists. There should be only one.
- wavelengths: The set of wavelengths included in the sequence.
- constraints: A set of the constraints required by the observation. In the case of an observation, this is just the (optional) constraints.
- program_used: We roll this information up from the atoms as it will be calculated during the GreedyMax algorithm. Note that it is also available directly from the OCS, which is used to populate the time allocation.
- partner_used: Same as above


Atom
----
Atom information, where an atom is the smallest schedulable set of steps such that useful science can be obtained from performing them.
Wavelengths must be specified in microns.

Attributes
^^^^^^^^^^
id
exec_time
prog_time
part_time
observed
qa_state
guide_state
resources
wavelengths


Target
------
Basic target information.

Attributes
^^^^^^^^^^
name
magnitudes
type

SiderealTarget
--------------
For a SiderealTarget, we have an RA and Dec and then proper motion information to calculate the exact position.
RA and Dec should be specified in decimal degrees. Proper motion must be specified in milliarcseconds / year. 
Epoch must be the decimal year.

Attributes
^^^^^^^^^^
ra
dec
pm_ra
pm_dec
epoch


NonsiderealTarget
-----------------
For a NonsiderealTarget, we have a HORIZONS designation to indicate the lookup information, a tag to determine the type 
of target, and arrays of ephemerides to specify the position.

Attributes
^^^^^^^^^^
des
tag 
ra 
dec

TargetType
----------
The type associated with a target in an observation.

BASE
USER
BLIND_OFFSET
OFF_AXIS
TUNING_STAR 
GUIDESTAR
OTHER = auto()


GuideSpeed
----------
How quickly a guider can guide on a guide star.

SLOW
MEDIUM
FAST

TargetTag
---------
A tag used by nonsidereal targets to indicate their type.

COMET
ASTEROID
MAJOR_BODY



Conditions
----------
A set of conditions.

- cc: CloudCover
- iq: ImageQuality
- sb: SkyBackground
- wv: WaterVapor

- least_restrictive: Return the least possible restrictive conditions.
- most_restrictive_conditions: Given an iterable of conditions, find the most restrictive amongst the set. If no conditions are given, return the most flexible conditions possible.


SkyBackground
-------------
Bins for observation sky background requirements or current conditions.

SB20
SB50
SB80
SBANY


CloudCover
----------
Bins for observation cloud cover requirements or current conditions.
   
CC50
CC70 
CC80
CCANY


ImageQuality
------------
Bins for observation image quality requirements or current conditions.

IQ20
IQ70
IQ85
IQANY


WaterVapor
----------
Bins for observation water vapor requirements or current conditions.

WV20
WV50
WV80
WVANY


Strehl
------
The Strehl ratio is a measure of the quality of optical image formation.
Used variously in situations where optical resolution is compromised due to lens aberrations or due to imaging
through the turbulent atmosphere, the Strehl ratio has a value between 0 and 1, with a hypothetical, perfectly
unaberrated optical system having a Strehl ratio of 1. (Source: Wikipedia.)

S00
S02
S04
S06
S08
S10 


ElevationType
-------------
The type of elevation constraints in the observing conditions.

NONE
HOUR_ANGLE
AIRMASS


Constraints
-----------
The constraints required for an observation to be performed.

- conditions
- elevation_type
- elevation_min
- elevation_max
- timing_windows
- strehl
- DEFAULT_AIRMASS_ELEVATION_MIN
- DEFAULT_AIRMASS_ELEVATION_MAX
Default airmass values to use for elevation constraints if:
  1. The Constraints are not present in the Observation at all; or
  2. The elevation_type is set to NONE.

Variant
-------
A weather variant.

- start_time
- iq
- cc
- wind_dir
- wind_spd: wind_speed should be in m / s.

MagnitudeSystem
---------------
List of magnitude systems associated with magnitude bands.

VEGA
AB
JY

MagnitudeBand
-------------

They are fully enumerated in MagnitudeBands, so they should be looked up by name there.
Values for center and width are specified in microns.

- name
- center
- width
- system
- description

Magnitude
---------
A magnitude value in a particular band.

- band
- value
- error


