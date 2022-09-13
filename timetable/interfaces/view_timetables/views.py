# Standard library imports
from string import ascii_uppercase

# Django imports
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader

# Local application imports
from data import models
from .utils import get_timetable_slot_indexed_timetable, get_summary_stats


@login_required
def selection_dashboard(request) -> HttpResponse:
    """View providing the context for the information displayed on the selection dashboard"""
    school_access_key = request.user.profile.school.school_access_key
    context = get_summary_stats(school_access_key=school_access_key)
    template = loader.get_template("selection_dashboard.html")
    return HttpResponse(template.render(context, request))


@login_required
def pupil_navigator(request) -> HttpResponse:
    """
    View to provide a dictionary of pupils which can be linked out to each of their timetables.
    This is pre-processed to be indexed by year group for display in the template.
    """
    school_id = request.user.profile.school.school_access_key
    year_indexed_pupils = {year: models.Pupil.objects.get_school_year_group(
        school_id=school_id, year_group=year).values() for year in models.Pupil.YearGroup.values}
    year_indexed_pupils = {key: value for key, value in year_indexed_pupils.items() if len(value) > 0}
    template = loader.get_template("pupils_navigator.html")
    context = {
        "all_pupils": year_indexed_pupils
    }
    return HttpResponse(template.render(context, request))


@login_required
def teacher_navigator(request) -> HttpResponse:
    """
    View to bring up a list of teachers which can be linked out to each of their timetables.
    Pre-processed to return a dictionary of teachers with the surnames indexed alphabetically.
    """
    school_id = request.user.profile.school.school_access_key
    alphabet = list(ascii_uppercase)
    teachers = {letter: models.Teacher.objects.get_teachers_surnames_starting_with_x(
        school_id=school_id, letter=letter).values() for letter in alphabet}
    teachers = {key: value for key, value in teachers.items() if len(value) > 0}
    template = loader.get_template("teachers_navigator.html")
    context = {
        "all_teachers": teachers
    }
    return HttpResponse(template.render(context, request))


@login_required
def pupil_timetable_view(request, id: int) -> HttpResponse:
    """
    View for the timetable of the individual pupil with the passed id.
    Context:
    ----------
    pupil - an instance of the Pupil model
    timetable - see _get_timetable_slot_indexed_timetable
    class_colours - a dictionary with keys of subject name strings, and values of hexadecimal colour strings
    """
    school_id = request.user.profile.school.school_access_key

    pupil = models.Pupil.objects.get_individual_pupil(school_id=school_id, pupil_id=id)
    classes = pupil.classes.all()
    timetable = get_timetable_slot_indexed_timetable(classes=classes)

    class_colours = {klass.subject_name: models.FixedClass.SubjectColour.get_colour_from_subject(
        subject_name=klass.subject_name) for klass in classes}
    class_colours[models.FixedClass.SubjectColour.FREE.name] = models.FixedClass.SubjectColour.FREE.label

    template = loader.get_template("pupil_timetable.html")
    context = {
        "pupil": pupil,
        "timetable": timetable,
        "class_colours": class_colours,
    }
    return HttpResponse(template.render(context, request))


@login_required
def teacher_timetable_view(request, id: int) -> HttpResponse:
    """
    View for the timetable of the individual teacher with the passed id.
    Context:
    ----------
        teacher - an instance of the teacher model
        timetable - see _get_timetable_slot_indexed_timetable
        class_colours - a dictionary with keys as year group integers, and values as hexadecimal colour strings
    """
    # noinspection PyUnresolvedReferences
    teacher = models.Teacher.objects.get_individual_teacher(school_id=123456, teacher_id=6)
    classes = teacher.classes.all()
    timetable = get_timetable_slot_indexed_timetable(classes=classes)

    year_group_colours = {}  # Not using dict comp here since info extraction requires some explanation
    for klass in classes:
        all_pupils = klass.pupils.all()
        if all_pupils.exists():  # Take first pupil from queryset since all have same year group
            first_pupil = klass.pupils.all()[0]
            year_group: int = first_pupil.year_group
            year_group_colours[year_group] = models.Pupil.YearGroup.get_colour_from_year_group(year_group=year_group)
    year_group_colours[models.FixedClass.SubjectColour.FREE.name] = models.FixedClass.SubjectColour.FREE.label
    year_group_colours[models.FixedClass.SubjectColour.LUNCH.name] = models.FixedClass.SubjectColour.LUNCH.label

    template = loader.get_template("teacher_timetable.html")
    context = {
        "teacher": teacher,
        "timetable": timetable,
        "colours": year_group_colours,
    }
    return HttpResponse(template.render(context, request))
