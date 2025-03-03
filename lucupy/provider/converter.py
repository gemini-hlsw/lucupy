from datetime import timedelta
from enum import Enum
from typing import List, Optional, TypeVar, Any, Type

import cattrs

__all__ = [
    'converter',
]


from lucupy.minimodel import ObservationClass, Observation, ObservationID, Priority, SetupTimeType, Target, Constraints, \
    ElevationType, ObservationStatus, ProgramID

E = TypeVar('E', bound=Enum)


def _timespan_to_timedelta(time_span: float) -> timedelta:
    return timedelta(seconds=time_span)

def register_enum_hooks(conv: cattrs.Converter) -> None:
    def structure_enum(value: str, cls: Type[E]) -> E:
        # Create a value-to-enum mapping
        value_map = {item.value: item for item in cls}
        match value:
            case v if v in value_map:
                return value_map[v]
            case _:
                raise ValueError(f"'{value}' is not a valid value for {cls.__name__}")

    # Register a generic hook factory for all Enum subclasses
    conv.register_structure_hook_factory(
        lambda cls: issubclass(cls, Enum) if isinstance(cls, type) else False,
        lambda cls: lambda v, _: structure_enum(v, cls)
    )


converter = cattrs.Converter()
register_enum_hooks(converter)



converter.register_structure_hook(
    Observation, lambda d, _: Observation(
        id=ObservationID(d['reference']['label']),
        internal_id=d['id'],
        order=None, # Comes from program
        title=d['title'],
        site=None,
        status=converter.structure(d['workflow']['state'],ObservationStatus),
        active=True, # linked to status, basically if status is not INACTIVE is false.
        priority=Priority.MEDIUM,
        setuptime_type=SetupTimeType.FULL,
        acq_overhead=_timespan_to_timedelta(d['execution']['digest']['setup']['full']['seconds']),
        obs_class=ObservationClass.NONE, # It's on atoms now, is it needed here?
        targets=[],
        guiding={},
        sequence=[],
        belongs_to=ProgramID(d['program']['id']),
        constraints=None,
    )
)
