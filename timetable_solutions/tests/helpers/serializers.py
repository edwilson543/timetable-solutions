"""
Helpers for dealing with serialized data.
These are used when testing for the expected serialized content of some test subject.
"""

# Standard library imports
from collections import OrderedDict

# Local application imports
from data import models
from interfaces.constants import UrlName


def expected_teacher(teacher: models.Teacher) -> OrderedDict:
    """Get the expected serialized data from a single teacher."""
    return OrderedDict(
        [
            ("teacher_id", teacher.teacher_id),
            ("firstname", teacher.firstname),
            ("surname", teacher.surname),
            ("title", teacher.title),
            ("lessons", [expected_lesson(lesson) for lesson in teacher.lessons.all()]),
            ("update_url", UrlName.TEACHER_UPDATE.url(teacher_id=teacher.teacher_id)),
        ]
    )


def expected_year_group(year_group: models.YearGroup) -> OrderedDict:
    """Get the expected serialized data from a single year group."""
    return OrderedDict(
        [
            ("year_group_id", year_group.year_group_id),
            ("year_group_name", year_group.year_group_name),
            ("number_pupils", year_group.get_number_pupils()),
        ]
    )


def expected_lesson(lesson: models.Lesson) -> OrderedDict:
    """Get the expected serialized data from a single year group."""
    return OrderedDict(
        [
            ("lesson_id", lesson.lesson_id),
            ("subject_name", lesson.subject_name),
            ("year_group", str(lesson.get_associated_year_group().year_group_name)),
            ("teacher", str(lesson.teacher)),
            ("total_required_slots", lesson.total_required_slots),
        ]
    )
