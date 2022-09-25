"""
Definition of dataclasses representing the models received by the serialiser.

Clearly this is unnecessary, given the solver is located in the domain layer of the project whose data layer defines the
models, however the solver is intentionally being implemented entirely independent of the core django project.
"""

# Standard library imports
from dataclasses import dataclass
import datetime as dt
from typing import List


@dataclass(frozen=True)
class FixedClass:
    """Dataclass containing fields of the FixedClass model instances included in the data provided by the API"""
    school: int
    class_id: str
    subject_name: str
    teacher: int | None
    classroom: int | None
    pupils: List[int]
    time_slots: List[int]
    user_defined: bool


@dataclass(frozen=True)
class UnsolvedClass:
    """Dataclass containing fields of the UnsolvedClass model instances included in the data provided by the API"""
    class_id: str
    subject_name: str
    teacher: int
    pupils: List[int]
    classroom : int
    total_slots: int
    min_distinct_slots: int


@dataclass(frozen=True)
class TimetableSlot:
    """Dataclass containing fields of the TimetableSlot model instances included in the data provided by the API"""
    slot_id: int
    day_of_week: str
    period_starts_at: dt.time
    period_duration: dt.timedelta
