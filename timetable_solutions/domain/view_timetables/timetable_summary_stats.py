"""
Module providing summary stats for the view timetable app's dashboard
"""

# Standard library imports
from typing import TypedDict, Literal

# Local application imports
from data import models
from domain.view_timetables.timetable_colours import TimetableColourAssigner


class StatsSummary(TypedDict):
    """
    Summary dict provided when the user has existing timetable solutions.
    """
    has_solutions: Literal[True]
    total_classes: int
    total_lessons: int
    total_pupils: int
    total_teachers: int
    busiest_days: list[str]
    busiest_days_pct: float
    quietest_days: list[str]
    quietest_days_pct: float
    busiest_times: list[str]
    busiest_times_pct: float


class NoStatsSummary(TypedDict):
    """
    Summary dict provided when the user DOES NOT have existing timetable solutions.
    """
    has_solutions: Literal[False]


def get_summary_stats_for_dashboard(school_access_key: int) -> StatsSummary | NoStatsSummary:
    """
    Function to extract some summary statistics on the timetable solutions that have been found, to be displayed on
    the selection_dashboard.
    :return - stats - a dictionary that gets added to the HTTP response context for the view_timetables' dashboard
    """
    # Call data layer to get required query sets
    all_lessons = models.Lesson.objects.get_all_instances_for_school(school_id=school_access_key)
    all_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=school_access_key)
    all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=school_access_key)
    all_teachers = models.Teacher.objects.get_all_instances_for_school(school_id=school_access_key)

    # High-level dict / stats used to calculate all other stats
    all_slot_lessons = {slot: slot.solver_lessons for slot in all_slots}
    slot_lesson_count = {
        slot: len([lesson for lesson in lessons.all() if  # Abuse of colour matcher, to avoid counting e.g. lunch
                   TimetableColourAssigner.check_lesson_for_colour_in_regex(lesson_name=lesson.subject_name) is None])
        for slot, lessons in all_slot_lessons.items()}

    distinct_lessons = len(all_lessons)
    total_lessons_taught = sum(slot_lesson_count.values())

    # Check whether there are in fact any summary stats to calculate
    if total_lessons_taught == 0:
        no_stats: NoStatsSummary = {
            "has_solutions": False
        }
        return no_stats

    # Stats relating to days of the week
    day_of_week_counts: dict[str, int] = {
        day.label: sum(total_lessons for slot, total_lessons in slot_lesson_count.items() if
                       # mypy thinks Weekday (an IntegerChoices subclass) is not iterable (no __iter__), but it is
                       slot.day_of_week == day.value) for day in models.WeekDay}  # type: ignore
    busiest_days = _get_dict_key_with_max_or_min_value(dictionary=day_of_week_counts, max_=True)
    busiest_days_pct = round(day_of_week_counts[busiest_days[0]] / total_lessons_taught, 2) * 100
    quietest_days = _get_dict_key_with_max_or_min_value(dictionary=day_of_week_counts, max_=False)
    quietest_days_pct = round(day_of_week_counts[quietest_days[0]] / total_lessons_taught, 2) * 100

    # Stats relating to times of day
    distinct_times = {slot.period_starts_at for slot in slot_lesson_count}
    time_of_day_counts = {time_of_day.strftime("%H:%M"):
                              sum(total_lessons for slot, total_lessons in slot_lesson_count.items() if
                                  slot.period_starts_at == time_of_day) for time_of_day in distinct_times
                          }
    busiest_times = _get_dict_key_with_max_or_min_value(dictionary=time_of_day_counts, max_=True)
    busiest_times_pct = round(time_of_day_counts[busiest_times[0]] / total_lessons_taught, 2) * 100

    # Summary dict
    stats: StatsSummary = {
        "has_solutions": True,  # We only reach this line if there are solutions

        "total_classes": distinct_lessons,
        "total_lessons": total_lessons_taught,
        "total_pupils": len(all_pupils),
        "total_teachers": len(all_teachers),

        "busiest_days": busiest_days,
        "busiest_days_pct": busiest_days_pct,
        "quietest_days": quietest_days,
        "quietest_days_pct": quietest_days_pct,

        "busiest_times": busiest_times,
        "busiest_times_pct": busiest_times_pct,
    }
    return stats


def _get_dict_key_with_max_or_min_value(dictionary: dict[str, int], max_: bool) -> list[str]:
    """
    Retrieve the key(s) in a dictionary that correspond to the maximum value.
    """
    if max_:
        value = max(dictionary.values())
    else:
        value = min(dictionary.values())
    return [key for key, val in dictionary.items() if value == val]
