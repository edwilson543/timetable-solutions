"""
Utility functions providing information that is sometimes needed by the interfaces layer, where this information
doesn't fit within the purpose of a specific domain component.
"""
# Standard library imports
from datetime import datetime
from typing import List

# Local application imports
from data import models


def get_user_timetable_slots(school_access_key: int) -> List:
    """
    Function to get the unique TIMES OF DAY that a given school has it's classes at
    :return times - ordered times of days when classes take place
    """
    slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=school_access_key)
    time_set = {slot.period_starts_at for slot in slots}
    times = sorted(list(time_set))
    return times
