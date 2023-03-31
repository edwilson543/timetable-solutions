"""
Queries focused on the school model relating to the solver.
"""

# Local application imports
from data import models


def check_school_has_sufficient_data_to_create_timetables(
    school: models.School,
) -> bool:
    """
    Test whether a school has sufficient data to attempt solving their timetabling problem.

    For now just a naive check that they have some data in each nevessary table.
    """
    return (
        school.has_teacher_data
        and school.has_pupil_data
        and school.has_classroom_data
        and school.has_year_group_data
        and school.has_timetable_structure_data
        and school.has_break_data
        and school.has_lesson_data
    )
