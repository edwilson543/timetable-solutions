"""
Functions used by the view_timetables app that extract data from the data layer, and then process it into a useful
format for a view to render in the template.
"""

# Standard library imports
from string import ascii_uppercase
from typing import Dict, List, Tuple, Union

# Django imports
from django.db.models import QuerySet

# Local application imports
from data import models


def get_summary_stats_for_dashboard(school_access_key: int) -> Dict:
    """
    Function to extract some summary statistics on the timetable solutions that have been found, to be displayed on
    the selection_dashboard
    """
    # Get the query sets used to create summary statistics
    all_classes = models.FixedClass.objects.get_non_user_defined_fixed_classes(school_id=school_access_key)

    all_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=school_access_key)
    all_slot_classes = {slot: slot.classes for slot in all_slots}
    slot_class_count = {key: len([klass for klass in klasses.all() if "LUNCH" not in klass.subject_name]) for
                        key, klasses in all_slot_classes.items()}

    pupils = models.Pupil.objects.get_all_instances_for_school(school_id=school_access_key)
    teachers = models.Teacher.objects.get_all_instances_for_school(school_id=school_access_key)

    stats = {
        "total_classes": len(all_classes),
        "total_lessons": sum(slot_class_count.values()),
        "busiest_slot": max(slot_class_count, key=slot_class_count.get),
        "total_pupils": len(pupils),
        "total_teachers": len(teachers),
    }
    return stats


def get_year_indexed_pupils(school_id: int) -> Dict[str, Union[QuerySet, List[models.Pupil]]]:
    """
    Function returning a dictionary of the pupils at a specific school, where the keys are the year groups, and the
    values the queryset of pupils in that year group.
    """
    year_indexed_pupils_unfiltered = {year: models.Pupil.objects.get_school_year_group(
        school_id=school_id, year_group=year).values() for year in models.Pupil.YearGroup.values}
    year_indexed_pupils = {key: value for key, value in year_indexed_pupils_unfiltered.items() if len(value) > 0}
    return year_indexed_pupils


def get_letter_indexed_teachers(school_id: int) -> Dict[str, Union[QuerySet, List[models.Teacher]]]:
    """
    Function returning a dictionary of the teachers at a specific school, where the keys are letters of the alphabet,
    and the values the queryset of teachers who's surname starts with that letter.
    """
    alphabet = list(ascii_uppercase)
    teachers_unfiltered = {letter: models.Teacher.objects.get_teachers_surnames_starting_with_x(
        school_id=school_id, letter=letter).values() for letter in alphabet}
    all_teachers = {key: value for key, value in teachers_unfiltered.items() if len(value) > 0}
    return all_teachers


def get_pupil_timetable_context(pupil_id: int, school_id: int) -> Tuple[models.Pupil, Dict, Dict]:
    """
    Function bundling together the data for populating the context dictionary in the pupil_timetable_view
    :return - pupil - an instance of the Pupil model
    :return - timetable - see get_timetable_slot_indexed_timetable
    :return - class_colours - see get_colours_for_pupil_timetable
    """
    pupil = models.Pupil.objects.get_individual_pupil(school_id=school_id, pupil_id=pupil_id)
    classes = pupil.classes.all()
    timetable_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=school_id)
    timetable = get_timetable_slot_indexed_timetable(classes=classes, timetable_slots=timetable_slots)
    timetable_colours = get_colours_for_pupil_timetable(classes=classes)
    return pupil, timetable, timetable_colours


def get_teacher_timetable_context(teacher_id: int, school_id: int) -> Tuple[models.Teacher, Dict, Dict]:
    """
    Function bundling together the data for populating the context dictionary in the teacher_timetable_view
    :return - pupil - an instance of the Teacher model
    :return - timetable - see get_timetable_slot_indexed_timetable
    :return - class_colours - see get_colours_for_teacher_timetable
    """
    teacher = models.Teacher.objects.get_individual_teacher(school_id=school_id, teacher_id=teacher_id)
    classes = teacher.classes.all()
    timetable_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=school_id)
    timetable = get_timetable_slot_indexed_timetable(classes=classes, timetable_slots=timetable_slots)
    timetable_colours = get_colours_for_teacher_timetable(classes=classes)
    return teacher, timetable, timetable_colours


# Functions called by get pupil / teacher timetable context
def get_timetable_slot_indexed_timetable(classes: Union[QuerySet, List[models.FixedClass]],
                                         timetable_slots: Union[QuerySet, List[models.TimetableSlot]]) -> Dict:
    """
    Function to return a timetable data structure that can easily be iterated over in a django template.

    Parameters:
        classes - this is a filtered QuerySet from the FixedClass model, for exactly 1 teacher/pupil
        timetable_slots - filtered QuerySet from the TimetableSlot model, specific to the teacher/pupil's school
    Returns: timetable - a nested dictionary where the outermost key is the time/period (9am/10am/...), the
    innermost key is the day of the week, and the values are the subject objects at each relevant timeslot, with the
    exception that a free period is just a string 'FREE'.
    e.g. {9AM: {MONDAY: MATHS, TUESDAY: FRENCH,...}, 10AM: {...}, ...}
    This structure is chosen such that it can be efficiently iterated over in the template to create a html table.
    """
    class_indexed_timetable = {klass: klass.time_slots.all().values() for klass in classes}
    period_start_times = {time_slot.period_starts_at for time_slot in timetable_slots}  # Use set to get unique times
    sorted_period_start_times = sorted(list(period_start_times))
    timetable = {}
    for time in sorted_period_start_times:
        time_timetable = {}  # specific times as indexes to nested dicts, indexed by days: {9AM: {Monday: [...]}...}
        for day in models.WeekDay.values:
            for klass, time_slots in class_indexed_timetable.items():
                queryset = time_slots.filter(day_of_week=day, period_starts_at=time)
                if queryset.exists():
                    time_timetable[day] = klass
            if day not in time_timetable:
                time_timetable[day] = models.FixedClass.SubjectColour.FREE.name
        timetable[time] = time_timetable
    return timetable


def get_colours_for_pupil_timetable(classes: Union[QuerySet, List[models.FixedClass]]) -> Dict:
    """
    Pupil timetables are colour coded using the FixedClass (one colour per FixedClass instance)
    :return A dictionary whose keys are subject names, and values are corresponding hexadecimal colour codes
    """
    class_colours = {klass.subject_name: models.FixedClass.SubjectColour.get_colour_from_subject(
        subject_name=klass.subject_name) for klass in classes}
    class_colours[models.FixedClass.SubjectColour.FREE.name] = models.FixedClass.SubjectColour.FREE.label
    return class_colours


def get_colours_for_teacher_timetable(classes: Union[QuerySet, List[models.FixedClass]]) -> Dict:
    """
    Pupil timetables are colour coded using the pupils' year group (one colour per pupil year group)
    :return A dictionary whose keys are year groups, and values are corresponding hexadecimal colour codes
    """
    year_group_colours = {}  # Not using dict comp here since info extraction requires some explanation
    for klass in classes:
        all_pupils = klass.pupils.all()
        if all_pupils.exists():  # Take first pupil from queryset since all have same year group
            first_pupil = klass.pupils.all()[0]
            year_group: int = first_pupil.year_group
            year_group_colours[year_group] = models.Pupil.YearGroup.get_colour_from_year_group(year_group=year_group)
    year_group_colours[models.FixedClass.SubjectColour.FREE.name] = models.FixedClass.SubjectColour.FREE.label
    year_group_colours[models.FixedClass.SubjectColour.LUNCH.name] = models.FixedClass.SubjectColour.LUNCH.label
    return year_group_colours
