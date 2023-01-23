"""
Functions used by the view_timetables app that extract data from the data layer, and then process it into a useful
format for a view to render in the template.
"""

# Standard library imports
import io
from string import ascii_uppercase

# Third party imports
import pandas as pd

# Local application imports
from data import constants
from data import models
from domain.view_timetables.timetable_colours import TimetableColourAssigner


# PUPIL / TEACHER NAVIGATOR PREPROCESSING
def get_pupil_year_groups(school_id: int) -> models.YearGroupQuerySet:
    """
    Get the pupils, grouped by year group, for a given school.
    Purpose: to iterate through in a django template.
    """
    return models.YearGroup.objects.get_all_year_groups_with_pupils(school_id=school_id)


def get_letter_indexed_teachers(school_id: int) -> dict[str, models.TeacherQuerySet]:
    """
    Function returning a dictionary of the teachers at a specific school, where the keys are letters of the alphabet,
    and the values the queryset of teachers with a surname starting with that letter.
    """
    alphabet = list(ascii_uppercase)
    teachers_unfiltered = {
        letter: models.Teacher.objects.get_teachers_surnames_starting_with_x(
            school_id=school_id, letter=letter
        ).values()
        for letter in alphabet
    }
    all_teachers = {
        key: value for key, value in teachers_unfiltered.items() if len(value) > 0
    }
    return all_teachers


# PUPIL / TEACHER TIMETABLE PREPROCESSING
def get_pupil_timetable_context(
    pupil_id: int, school_id: int
) -> tuple[models.Pupil, dict, dict]:
    """
    Function bundling together the data for populating the context dictionary in the pupil_timetable_view
    :return - pupil - an instance of the Pupil model
    :return - timetable - see get_timetable_slot_indexed_timetable
    :return - timetable_colours - see get_colours_for_pupil_timetable on the TimetableColourAssigner Enum
    """
    pupil = models.Pupil.objects.get_individual_pupil(
        school_id=school_id, pupil_id=pupil_id
    )
    lessons = pupil.lessons.all()
    timetable_slots = models.TimetableSlot.objects.get_all_instances_for_school(
        school_id=school_id
    )
    timetable = get_timetable_slot_indexed_timetable(
        lessons=lessons, timetable_slots=timetable_slots
    )
    timetable_colours = TimetableColourAssigner.get_colours_for_pupil_timetable(
        lessons=lessons
    )
    return pupil, timetable, timetable_colours


def get_teacher_timetable_context(
    teacher_id: int, school_id: int
) -> tuple[models.Teacher, dict, dict]:
    """
    Function bundling together the data for populating the context dictionary in the teacher_timetable_view
    :return - pupil - an instance of the Teacher model
    :return - timetable - see get_timetable_slot_indexed_timetable
    :return - timetable_colours - see get_colours_for_teacher_timetable on the TimetableColourAssigner Enum
    """
    teacher = models.Teacher.objects.get_individual_teacher(
        school_id=school_id, teacher_id=teacher_id
    )
    lessons = teacher.lessons.all()
    timetable_slots = models.TimetableSlot.objects.get_all_instances_for_school(
        school_id=school_id
    )
    timetable = get_timetable_slot_indexed_timetable(
        lessons=lessons, timetable_slots=timetable_slots
    )
    timetable_colours = TimetableColourAssigner.get_colours_for_teacher_timetable(
        lessons=lessons
    )
    return teacher, timetable, timetable_colours


def get_pupil_timetable_as_csv(
    pupil_id: int, school_id: int
) -> tuple[models.Pupil, io.StringIO]:
    """
    Function to retrieve a specific pupil's timetable as a csv.
    :return pupil - the instance of the Pupil model in question
    :return csv_buffer - buffer storing the csv file representing the pupil's timetable
    """
    pupil = models.Pupil.objects.get_individual_pupil(
        school_id=school_id, pupil_id=pupil_id
    )
    lessons = pupil.lessons.all()
    timetable_slots = models.TimetableSlot.objects.get_all_instances_for_school(
        school_id=school_id
    )
    csv_buffer = get_timetable_as_csv(lessons=lessons, timetable_slots=timetable_slots)
    return pupil, csv_buffer


def get_teacher_timetable_as_csv(
    teacher_id: int, school_id: int
) -> tuple[models.Teacher, io.StringIO]:
    """
    Function to retrieve a specific teacher's timetable as a csv.
    :return teacher - the instance of the Teacher model in question
    :return csv_buffer - buffer storing the csv file representing the teacher's timetable
    """
    teacher = models.Teacher.objects.get_individual_teacher(
        school_id=school_id, teacher_id=teacher_id
    )
    lessons = teacher.lessons.all()
    timetable_slots = models.TimetableSlot.objects.get_all_instances_for_school(
        school_id=school_id
    )
    csv_buffer = get_timetable_as_csv(lessons=lessons, timetable_slots=timetable_slots)
    return teacher, csv_buffer


# Generalised functions providing timetable for context / csv files
def get_timetable_as_csv(
    lessons: models.LessonQuerySet, timetable_slots: models.TimetableSlotQuerySet
) -> io.StringIO:
    """
    Function to create a pupil / teacher timetable as a csv file.
    We just call the get_timetable_slot_indexed_timetable, and process the dictionary into a DataFrame.
    """
    timetable_dict = get_timetable_slot_indexed_timetable(
        lessons=lessons, timetable_slots=timetable_slots, get_subject_name=True
    )

    # Process timetable into DataFrame
    timetable_df = pd.DataFrame.from_dict(timetable_dict)
    timetable_df = timetable_df.transpose()
    timetable_df = timetable_df.applymap(str.title)
    timetable_df.index.name = "Time"

    # Process DataFrame into buffer
    csv_buffer = io.StringIO()
    timetable_df.to_csv(csv_buffer)
    csv_buffer.seek(0)
    return csv_buffer


def get_timetable_slot_indexed_timetable(
    lessons: models.LessonQuerySet,
    timetable_slots: models.TimetableSlotQuerySet,
    get_subject_name: bool = False,
) -> dict:
    """
    Function defining a data structure for pupil / teacher timetables that can easily be iterated over in a django
    template to create a html table.

    Parameters:
        lessons - this is a filtered QuerySet from the Lesson model, for exactly 1 teacher/pupil
        timetable_slots - filtered QuerySet from the TimetableSlot model, specific to the teacher/pupil's school
        get_subject_name - whether to return the Lessons instances, or just the subject name. Defaults to returning
                            the full lessons instances

    Returns: timetable - a nested dictionary where the outermost key is the time/period (9am/10am/...), the
    innermost key is the day of the week, and the values are the subject objects at each relevant timeslot, with the
    exception that a free period is just a string 'FREE'.
    e.g. {9AM: {MONDAY: MATHS, TUESDAY: FRENCH,...}, 10AM: {...}, ...}
    """
    lesson_indexed_timetable = {
        lesson: lesson.get_all_time_slots() for lesson in lessons
    }
    period_start_times = {
        (time_slot.period_starts_at, time_slot.period_ends_at)
        for time_slot in timetable_slots
    }
    sorted_period_start_times = sorted(
        list(period_start_times), key=lambda tup: tup[0]
    )  # Sort by start time

    timetable = {}
    for start_time, end_time in sorted_period_start_times:
        time_timetable = (
            {}
        )  # specific times as indexes to nested dicts, indexed by days: {9AM: {Monday: [...]}...}

        for day in constants.Day.values:
            day_label = constants.Day(day).label
            for lesson, time_slots in lesson_indexed_timetable.items():
                queryset = time_slots.filter(
                    day_of_week=day, period_starts_at=start_time
                )
                if queryset.exists():  # Pupil / teacher has a lesson at this time
                    if get_subject_name:
                        time_timetable[day_label] = lesson.subject_name
                    else:
                        time_timetable[day_label] = lesson
            if day_label not in time_timetable:
                time_timetable[day_label] = TimetableColourAssigner.Colour.FREE.name

        time_string = start_time.strftime("%H:%M") + "-" + end_time.strftime("%H:%M")
        timetable[time_string] = time_timetable
    return timetable
