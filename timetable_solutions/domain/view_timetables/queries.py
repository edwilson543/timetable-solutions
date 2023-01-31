# Local application imports
from collections import OrderedDict
from string import ascii_uppercase

# Local application imports
from data import constants as data_constants
from data import models
from domain.view_timetables import timetable
from domain.view_timetables import timetable_component


def get_pupil_timetable(
    pupil: models.Pupil,
) -> OrderedDict[data_constants.Day, list[timetable_component.TimetableComponent]]:
    """
    Retrieve a timetable for an individual pupil.

    :return OrderedDict, whose key/value pairs are the pupil's timetable for each
    day of the week, including lessons, breaks and free periods.
    """
    lessons = pupil.lessons.all()
    breaks = pupil.year_group.breaks.all()
    tt = timetable.Timetable(lessons=lessons, breaks=breaks)
    return tt.make_timetable()


def get_teacher_timetable(
    teacher: models.Teacher,
) -> OrderedDict[data_constants.Day, list[timetable_component.TimetableComponent]]:
    """
    Retrieve a timetable for an individual teacher.

    :return OrderedDict, whose key/value pairs are the teacher's timetable for each
    day of the week, including lessons, breaks and free periods.
    """
    lessons = teacher.lessons.all()
    breaks = teacher.breaks.all()
    tt = timetable.Timetable(lessons=lessons, breaks=breaks)
    return tt.make_timetable()


def get_letter_indexed_teachers(school_id: int) -> dict[str, models.TeacherQuerySet]:
    """Get a dictionary mapping letters of the alphabet to teachers whose surname starts with that letter."""
    alphabet = list(ascii_uppercase)
    teachers_unfiltered = {
        letter: models.Teacher.objects.get_teachers_surnames_starting_with_x(
            school_id=school_id, letter=letter
        )
        for letter in alphabet
    }
    all_teachers = {
        key: value for key, value in teachers_unfiltered.items() if len(value) > 0
    }
    return all_teachers
