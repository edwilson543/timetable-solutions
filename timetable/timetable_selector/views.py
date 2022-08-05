# Django imports
from django.http import HttpResponse
from django.template import loader

# Local application imports
from .models import Pupil, Teacher, FixedClass
from .utils import _get_timetable_slot_indexed_timetable


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
    Pre-processed to return a dictionary of teachers with the surnames indexed alphabetically.
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
    pupil - an instance of the Pupil model
    timetable - see _get_timetable_slot_indexed_timetable
    class_colours - a dictionary with keys of subject name strings, and values of hexadecimal colour strings
    """
    # noinspection PyUnresolvedReferences
    pupil = Pupil.objects.get(id=id)
    classes = pupil.classes.all()
    timetable = _get_timetable_slot_indexed_timetable(classes=classes)

    class_colours = {klass.subject_name: FixedClass.SubjectColour.get_colour_from_subject(
        subject_name=klass.subject_name) for klass in classes}
    class_colours[FixedClass.SubjectColour.FREE.name] = FixedClass.SubjectColour.FREE.value

    template = loader.get_template("pupil_timetable.html")
    context = {
        "pupil": pupil,
        "timetable": timetable,
        "class_colours": class_colours,
    }
    return HttpResponse(template.render(context, request))


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
    teacher = Teacher.objects.get(id=id)
    classes = teacher.classes.all()
    timetable = _get_timetable_slot_indexed_timetable(classes=classes)

    year_group_colours = {}  # Not using dict comp here since info extraction requires some explanation
    for klass in classes:
        all_pupils = klass.pupils.all()
        if all_pupils.exists():  # Take first pupil from queryset since all have same year group
            first_pupil = klass.pupils.all()[0]
            year_group: int = first_pupil.year_group
            year_group_colours[year_group] = Pupil.YearGroup.get_colour_from_year_group(year_group=year_group)
    year_group_colours[FixedClass.SubjectColour.FREE.name] = FixedClass.SubjectColour.FREE.value
    year_group_colours[FixedClass.SubjectColour.LUNCH.name] = FixedClass.SubjectColour.LUNCH.value

    template = loader.get_template("teacher_timetable.html")
    context = {
        "teacher": teacher,
        "timetable": timetable,
        "colours": year_group_colours,
    }
    return HttpResponse(template.render(context, request))
