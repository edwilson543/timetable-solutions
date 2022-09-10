"""Utility functions called by more than one view."""

# Standard library imports
from typing import Dict, List

# Django imports
from django.db.models import QuerySet

# Local application imports
from data import models


# noinspection PyUnresolvedReferences
def get_summary_stats(school_access_key: int) -> Dict:
    """
    Function to extract some summary statistics on the timetable solutions that have been found, to be displayed on
    the selection_dashboard
    """
    school = models.School.objects.get_individual_school(school_id=school_access_key)  # TODO remove

    # Get the query sets used to create summary statistics
    all_classes = models.FixedClass.objects.get_non_user_defined_fixed_classes(school_id=school_access_key)

    all_slots = models.TimetableSlot.objects.filter(school=school)
    all_slot_classes = {slot: slot.classes for slot in all_slots}
    slot_class_count = {key: len([klass for klass in klasses.all() if "LUNCH" not in klass.subject_name]) for
                        key, klasses in all_slot_classes.items()}

    pupils = models.Pupil.objects.get_all_school_pupils(school_id=school_access_key)
    teachers = models.Teacher.objects.get_all_school_teachers(school_id=school_access_key)

    stats = {
        "total_classes": len(all_classes),
        "total_lessons": sum(slot_class_count.values()),
        "busiest_slot": max(slot_class_count, key=slot_class_count.get),
        "total_pupils": len(pupils),
        "total_teachers": len(teachers),
    }
    return stats


def get_timetable_slot_indexed_timetable(classes: QuerySet | List[models.FixedClass]) -> Dict:
    """
    Function to return a timetable data structure that can easily be iterated over in a django template.

    Parameters: classes - this is a filtered QuerySet from the FixedClass model, for exactly 1 teacher/pupil
    Returns: timetable - a nested dictionary where the outermost key is the time/period (9am/10am/...), the
    innermost key is the day of the week, and the values are the subject objects at each relevant timeslot, with the
    exception that a free period is just a string 'FREE'.
    e.g. {9AM: {MONDAY: MATHS, TUESDAY: FRENCH,...}, 10AM: {...}, ...}
    This structure is chosen such that it can be efficiently iterated over in the template to create a html table.
    """
    class_indexed_timetable = {klass: klass.time_slots.all().values() for klass in classes}
    timetable = {}
    for time in models.TimetableSlot.PeriodStart.values:
        time_timetable = {}  # specific times as indexes to nested dicts, indexed by days: {9AM: {Monday: [...]}...}
        for day in models.TimetableSlot.WeekDay.values:
            # noinspection PyUnresolvedReferences
            for klass, time_slots in class_indexed_timetable.items():
                queryset = time_slots.filter(day_of_week=day, period_starts_at=time)
                if queryset.exists():
                    time_timetable[day] = klass
            if day not in time_timetable:
                time_timetable[day] = models.FixedClass.SubjectColour.FREE.name
        timetable[time] = time_timetable
    return timetable
