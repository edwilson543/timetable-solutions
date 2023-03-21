"""
Helpers for dealing with serialized data.
These are used when testing for the expected serialized content of some test subject.
"""

# Standard library imports
from collections import OrderedDict

# Local application imports
from data import constants, models
from interfaces.constants import UrlName


def expected_year_group(year_group: models.YearGroup) -> OrderedDict:
    """
    Get the expected serialized data from a single year group.
    """
    return OrderedDict(
        [
            ("year_group_id", year_group.year_group_id),
            ("year_group_name", year_group.year_group_name),
            ("number_pupils", year_group.get_number_pupils()),
            (
                "update_url",
                UrlName.YEAR_GROUP_UPDATE.url(year_group_id=year_group.year_group_id),
            ),
        ]
    )


def expected_lesson(lesson: models.Lesson) -> OrderedDict:
    """
    Get the expected serialized data from a single lesson.
    """

    def _teacher() -> dict[str, str]:
        if lesson.teacher:
            return {
                "name": str(lesson.teacher),
                "url": UrlName.TEACHER_UPDATE.url(teacher_id=lesson.teacher.teacher_id),
            }
        else:
            return {}

    def _classroom() -> dict[str, str]:
        if lesson.classroom:
            return {
                "name": str(lesson.classroom),
                "url": UrlName.CLASSROOM_UPDATE.url(
                    classroom_id=lesson.classroom.classroom_id
                ),
            }
        else:
            return {}

    return OrderedDict(
        [
            ("lesson_id", lesson.lesson_id),
            ("subject_name", lesson.subject_name),
            ("year_group", str(lesson.get_associated_year_group().year_group_name)),
            ("teacher", _teacher()),
            ("classroom", _classroom()),
            ("total_required_slots", lesson.total_required_slots),
        ]
    )


def expected_teacher(teacher: models.Teacher) -> OrderedDict:
    """
    Get the expected serialized data from a single teacher.
    """
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


def expected_classroom(classroom: models.Classroom) -> OrderedDict:
    """
    Get the expected serialized data from a single classroom.
    """
    return OrderedDict(
        [
            ("classroom_id", classroom.classroom_id),
            ("building", classroom.building),
            ("room_number", classroom.room_number),
            (
                "lessons",
                [expected_lesson(lesson) for lesson in classroom.lessons.all()],
            ),
            (
                "update_url",
                UrlName.CLASSROOM_UPDATE.url(classroom_id=classroom.classroom_id),
            ),
        ]
    )


def expected_pupil(pupil: models.Pupil) -> OrderedDict:
    """
    Get the expected serialized data from a single pupil.
    """
    return OrderedDict(
        [
            ("pupil_id", pupil.pupil_id),
            ("firstname", pupil.firstname),
            ("surname", pupil.surname),
            ("year_group", pupil.year_group.year_group_name),
            ("lessons", [expected_lesson(lesson) for lesson in pupil.lessons.all()]),
            ("update_url", UrlName.PUPIL_UPDATE.url(pupil_id=pupil.pupil_id)),
        ]
    )


def expected_slot(slot: models.TimetableSlot) -> OrderedDict:
    """
    Get the expected serialized data from a single timetable slot.
    """
    return OrderedDict(
        [
            ("slot_id", slot.slot_id),
            ("day_of_week", constants.Day(slot.day_of_week).label),
            ("starts_at", slot.starts_at.strftime("%H:%M")),
            ("ends_at", slot.ends_at.strftime("%H:%M")),
            (
                "relevant_year_groups",
                [expected_year_group(yg) for yg in slot.relevant_year_groups.all()],
            ),
            ("update_url", UrlName.TIMETABLE_SLOT_UPDATE.url(slot_id=slot.slot_id)),
        ]
    )
