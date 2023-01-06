"""
Convenience imports for objects form view_timetables domain component
"""
from .timetable_constructor import (
    get_pupil_year_groups,
    get_letter_indexed_teachers,
    get_pupil_timetable_context,
    get_teacher_timetable_context,
    get_pupil_timetable_as_csv,
    get_teacher_timetable_as_csv,
)
from .timetable_summary_stats import get_summary_stats_for_dashboard
from .timetable_colours import TimetableColourAssigner
