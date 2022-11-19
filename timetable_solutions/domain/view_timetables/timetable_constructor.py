"""
Functions used by the view_timetables app that extract data from the data layer, and then process it into a useful
format for a view to render in the template.
"""

# Standard library imports
import datetime as dt
import io
from string import ascii_uppercase
from typing import Dict, Tuple

# Third party imports
import pandas as pd

# Local application imports
from data import models
from domain.view_timetables.timetable_colours import TimetableColourAssigner


# PUPIL / TEACHER NAVIGATOR PREPROCESSING
def get_year_indexed_pupils(school_id: int) -> Dict[str, models.PupilQuerySet]:
    """
    Function returning a dictionary of the pupils at a specific school, where the keys are the year groups, and the
    values the queryset of pupils in that year group.
    """
    year_indexed_pupils_unfiltered = {year: models.Pupil.objects.get_school_year_group(
        school_id=school_id, year_group=year).values() for year in models.Pupil.YearGroup.values}
    year_indexed_pupils = {key: value for key, value in year_indexed_pupils_unfiltered.items() if len(value) > 0}
    return year_indexed_pupils


def get_letter_indexed_teachers(school_id: int) -> Dict[str, models.TeacherQuerySet]:
    """
    Function returning a dictionary of the teachers at a specific school, where the keys are letters of the alphabet,
    and the values the queryset of teachers who's surname starts with that letter.
    """
    alphabet = list(ascii_uppercase)
    teachers_unfiltered = {letter: models.Teacher.objects.get_teachers_surnames_starting_with_x(
        school_id=school_id, letter=letter).values() for letter in alphabet}
    all_teachers = {key: value for key, value in teachers_unfiltered.items() if len(value) > 0}
    return all_teachers


# PUPIL / TEACHER TIMETABLE PREPROCESSING
def get_pupil_timetable_context(pupil_id: int, school_id: int) -> Tuple[models.Pupil, Dict, Dict]:
    """
    Function bundling together the data for populating the context dictionary in the pupil_timetable_view
    :return - pupil - an instance of the Pupil model
    :return - timetable - see get_timetable_slot_indexed_timetable
    :return - class_colours - see get_colours_for_pupil_timetable on the TimetableColourAssigner Enum
    """
    pupil = models.Pupil.objects.get_individual_pupil(school_id=school_id, pupil_id=pupil_id)
    classes = pupil.classes.all()
    timetable_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=school_id)
    timetable = get_timetable_slot_indexed_timetable(classes=classes, timetable_slots=timetable_slots)
    timetable_colours = TimetableColourAssigner.get_colours_for_pupil_timetable(classes=classes)
    return pupil, timetable, timetable_colours


def get_teacher_timetable_context(teacher_id: int, school_id: int) -> Tuple[models.Teacher, Dict, Dict]:
    """
    Function bundling together the data for populating the context dictionary in the teacher_timetable_view
    :return - pupil - an instance of the Teacher model
    :return - timetable - see get_timetable_slot_indexed_timetable
    :return - class_colours - see get_colours_for_teacher_timetable on the TimetableColourAssigner Enum
    """
    teacher = models.Teacher.objects.get_individual_teacher(school_id=school_id, teacher_id=teacher_id)
    classes = teacher.classes.all()
    timetable_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=school_id)
    timetable = get_timetable_slot_indexed_timetable(classes=classes, timetable_slots=timetable_slots)
    timetable_colours = TimetableColourAssigner.get_colours_for_teacher_timetable(classes=classes)
    return teacher, timetable, timetable_colours


def get_pupil_timetable_as_csv(pupil_id: int, school_id: int) -> Tuple[models.Pupil, io.StringIO]:
    """
    Function to retrieve a specific pupil's timetable as a csv.
    :return pupil - the instance of the Pupil model in question
    :return csv_buffer - buffer storing the csv file representing the pupil's timetable
    """
    pupil = models.Pupil.objects.get_individual_pupil(school_id=school_id, pupil_id=pupil_id)
    classes = pupil.classes.all()
    timetable_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=school_id)
    csv_buffer = get_timetable_as_csv(classes=classes, timetable_slots=timetable_slots)
    return pupil, csv_buffer


# Generalised functions providing timetable for context / csv files
def get_timetable_as_csv(classes: models.FixedClassQuerySet,
                         timetable_slots: models.TimetableSlotQuerySet) -> io.StringIO:
    """
    Function to create a pupil / teacher timetable as a csv file.
    We just call the get_timetable_slot_indexed_timetable, and process the dictionary into a DataFrame.
    """
    timetable_dict = get_timetable_slot_indexed_timetable(
        classes=classes, timetable_slots=timetable_slots, get_subject_name=True)

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


def get_timetable_slot_indexed_timetable(classes: models.FixedClassQuerySet,
                                         timetable_slots: models.TimetableSlotQuerySet,
                                         get_subject_name: bool = False) -> Dict:
    """
    Function defining a data structure for pupil / teacher timetables that can easily be iterated over in a django
    template to create a html table.

    Parameters:
        classes - this is a filtered QuerySet from the FixedClass model, for exactly 1 teacher/pupil
        timetable_slots - filtered QuerySet from the TimetableSlot model, specific to the teacher/pupil's school
        get_subject_name - whether to return the FixedClass instances, or just the subject name. Default to returning
                            the full fixed class instance

    Returns: timetable - a nested dictionary where the outermost key is the time/period (9am/10am/...), the
    innermost key is the day of the week, and the values are the subject objects at each relevant timeslot, with the
    exception that a free period is just a string 'FREE'.
    e.g. {9AM: {MONDAY: MATHS, TUESDAY: FRENCH,...}, 10AM: {...}, ...}
    """
    class_indexed_timetable = {klass: klass.time_slots.all() for klass in classes}
    period_start_times = {(time_slot.period_starts_at, time_slot.period_duration) for time_slot in timetable_slots}
    sorted_period_start_times = sorted(list(period_start_times))

    timetable = {}
    for start_time, duration in sorted_period_start_times:
        time_timetable = {}  # specific times as indexes to nested dicts, indexed by days: {9AM: {Monday: [...]}...}

        for day in models.WeekDay.values:
            day_label = models.WeekDay(day).label
            for klass, time_slots in class_indexed_timetable.items():
                queryset = time_slots.filter(day_of_week=day, period_starts_at=start_time)
                if queryset.exists():  # Pupil / teacher has a class at this time
                    if get_subject_name:
                        time_timetable[day_label] = klass.subject_name
                    else:
                        time_timetable[day_label] = klass
            if day_label not in time_timetable:
                time_timetable[day_label] = TimetableColourAssigner.Colour.FREE.name

        end_time = dt.datetime.combine(date=dt.datetime.min, time=start_time) + duration
        time_string = start_time.strftime("%H:%M") + "-" + end_time.strftime("%H:%M")
        timetable[time_string] = time_timetable
    return timetable
