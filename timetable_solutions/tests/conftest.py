"""
Conftest.py file specifies pytest fixtures shared by more than one test module.
"""

# Standard library imports
import datetime as dt
from typing import List

# Third party imports
import pytest

# Local application imports
from domain.solver.constants import school_dataclasses


# SIMULATED INPUT DATA FOR THE SOLVER
@pytest.fixture(scope="class")
def fixed_class_data() -> List[school_dataclasses.FixedClass]:
    """Dummy fixed class data to be added to the input data loader, for testing meta data extraction"""
    fc1 = school_dataclasses.FixedClass(school=1, class_id="A", teacher=1, pupils=[1, 2], classroom=1,
                                        time_slots=[1, 2], subject_name="Maths", user_defined=True)
    fc2 = school_dataclasses.FixedClass(school=1, class_id="B", teacher=2, pupils=[3, 4], classroom=2,
                                        time_slots=[3, 4], subject_name="English", user_defined=True)
    return [fc1, fc2]


@pytest.fixture(scope="class")
def unsolved_class_data() -> List[school_dataclasses.UnsolvedClass]:
    """Dummy unsolved class data to be added to the input data loader, for testing meta data extraction"""
    uc1 = school_dataclasses.UnsolvedClass(class_id="A", teacher=1, pupils=[1, 2], classroom=1, total_slots=3,
                                           subject_name="Maths", min_distinct_slots=3)
    uc2 = school_dataclasses.UnsolvedClass(class_id="B", teacher=2, pupils=[3, 4], classroom=2, total_slots=2,
                                           subject_name="English", min_distinct_slots=3)
    return [uc1, uc2]


@pytest.fixture(scope="class")
def timetable_slot_data() -> List[school_dataclasses.TimetableSlot]:
    """Dummy timetable slot data to be added to the input data loader, for testing meta data extraction"""
    slot_1 = school_dataclasses.TimetableSlot(
        slot_id=1, day_of_week="MONDAY", period_starts_at=dt.time(hour=9), period_duration=dt.timedelta(hours=1))
    slot_2 = school_dataclasses.TimetableSlot(
        slot_id=2, day_of_week="MONDAY", period_starts_at=dt.time(hour=10), period_duration=dt.timedelta(hours=1))
    slot_3 = school_dataclasses.TimetableSlot(
        slot_id=3, day_of_week="TUESDAY", period_starts_at=dt.time(hour=9), period_duration=dt.timedelta(hours=1))
    slot_4 = school_dataclasses.TimetableSlot(
        slot_id=4, day_of_week="TUESDAY", period_starts_at=dt.time(hour=10), period_duration=dt.timedelta(hours=1))
    return [slot_1, slot_2, slot_3, slot_4]
