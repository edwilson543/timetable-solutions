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
            ("update_url", UrlName.TEACHER_UPDATE.url(teacher_id=teacher.teacher_id)),
            # Since these helpers will be deleted, do not include an actual timetable url
            ("timetable_url", ""),
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


def expected_break(break_: models.Break) -> OrderedDict:
    """
    Get the expected serialized data from a single break.
    """
    return OrderedDict(
        [
            ("break_id", break_.break_id),
            ("break_name", break_.break_name),
            ("day_of_week", constants.Day(break_.day_of_week).label),
            ("starts_at", break_.starts_at.strftime("%H:%M")),
            ("ends_at", break_.ends_at.strftime("%H:%M")),
            (
                "relevant_year_groups",
                [expected_year_group(yg) for yg in break_.relevant_year_groups.all()],
            ),
            (
                "teachers",
                [expected_teacher(teacher) for teacher in break_.teachers.all()],
            ),
            ("update_url", UrlName.BREAK_UPDATE.url(break_id=break_.break_id)),
        ]
    )
