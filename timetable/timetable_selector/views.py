# Standard library imports
from typing import Dict, List, Tuple

# Django imports
from django.db.models import QuerySet
from django.http import HttpResponse
from django.template import loader

# Local application imports
from .models import Pupil, Teacher, TimetableSlot, FixedClass


def selection_navigator(request) -> HttpResponse:
    """View to bring up the main navigation screen for guiding the user towards individual timetables."""
    template = loader.get_template("selection_navigator.html")
    return HttpResponse(template.render({}, request))


def pupil_navigator(request) -> HttpResponse:
    """
    View to provide a dictionary of pupils which can be linked out to each of their timetables.
    This is pre-processed to be indexed by year group for display in the template.
    """
    # noinspection PyUnresolvedReferences
    year_indexed_pupils = {year: Pupil.objects.filter(year_group=year).order_by("surname").values() for
                           year in Pupil.YearGroup.values}
    year_indexed_pupils = {key: value for key, value in year_indexed_pupils.items() if len(value) > 0}
    template = loader.get_template("pupils_navigator.html")
    context = {
        "all_pupils": year_indexed_pupils
    }
    return HttpResponse(template.render(context, request))


def teacher_navigator(request) -> HttpResponse:
    """
    View to bring up a list of teachers which can be linked out to each of their timetables.
    Pre-processed to return a dictionary of teachers with the surnmaes indexed alphabetically.
    """
    alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    # noinspection PyUnresolvedReferences
    teachers = {letter: Teacher.objects.filter(surname__startswith=letter).order_by("firstname").values() for
                letter in alphabet}
    teachers = {key: value for key, value in teachers.items() if len(value) > 0}
    template = loader.get_template("teachers_navigator.html")
    context = {
        "all_teachers": teachers
    }
    return HttpResponse(template.render(context, request))


def pupil_timetable_view(request, id: int) -> HttpResponse:
    """
    View for the timetable of the individual pupil with the passed id.
    Context:
    ----------
    timetable - see _get_timetable_slot_indexed_timetable
    pupil - an instance of the Pupil model
    class_colours - a dictionary
    """
    # noinspection PyUnresolvedReferences
    pupil = Pupil.objects.get(id=id)
    classes = pupil.classes.all()
    timetable = _get_timetable_slot_indexed_timetable(classes=classes)

    class_colours = {klass.subject_name: FixedClass.SubjectColour.get_colour_from_subject(
        subject_name=klass.subject_name) for klass in classes}
    class_colours = class_colours | {f"FREE": FixedClass.SubjectColour.get_colour_from_subject(
            FixedClass.SubjectColour.FREE.name)}

    template = loader.get_template("pupil_timetable.html")
    context = {
        "timetable": timetable,
        "pupil": pupil,
        "class_colours": class_colours,
    }
    return HttpResponse(template.render(context, request))


def teacher_timetable_view(request, id: int) -> HttpResponse:
    """
    View for the timetable of the individual teacher with the passed id.
    Context is as for the pupil timetable view.
    """
    # TODO first split out the reusable part of the pupil timetable view.
    # For the template, create a css file for the timetable.
    pass


def _get_timetable_slot_indexed_timetable(classes: QuerySet | List[FixedClass]) -> \
        Dict[Tuple[TimetableSlot.PeriodStart, TimetableSlot.WeekDay] | str, QuerySet | List[FixedClass]]:
    """
    Function to return a timetable data structure that can easily be iterated over in a django template.

    Parameters: classes - this is a filtered QuerySet from the FixedClass model, for exactly 1 teacher/pupil
    Returns: timetable - a nested dictionary where the outermost key is the time/period (9am/10am/...), the
    innermost key is the day of the week, and the values are the subject objects at each relevant timeslot, with the
    exception that a free period is just a string 'FREE'.
    e.g. {9AM: {MONDAY: MATHS, TUESDAY: FRENCH,...}, 10AM: {...}, ...}
    This structure is chosen such that it can be efficiently iterated over in the template to create a html table.
    """
    class_indexed_timetable = {klass: klass.time_slots.all().values() for klass in classes}
    timetable = {}
    for time in TimetableSlot.PeriodStart.values:
        time_timetable = {}  # specific times as indexes to nested dicts, indexed by days: {9AM: {Monday: [...]}...}
        for day in TimetableSlot.WeekDay.values:
            # noinspection PyUnresolvedReferences
            for klass, time_slots in class_indexed_timetable.items():
                queryset = time_slots.filter(day_of_week=day, period_start_time=time)
                if queryset.exists():
                    time_timetable[day] = klass
            if day not in time_timetable:
                time_timetable[day] = FixedClass.SubjectColour.FREE.name
        timetable[time] = time_timetable
    return timetable
