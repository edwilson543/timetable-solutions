"""Views used to navigate users towards an individual pupil/teacher's timetable."""

# Django imports
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader

# Local application imports
from domain import view_timetables


@login_required
def selection_dashboard(request) -> HttpResponse:
    """View providing the context for the information displayed on the selection dashboard"""
    school_access_key = request.user.profile.school.school_access_key
    context = view_timetables.timetable_summary_stats.get_summary_stats_for_dashboard(
        school_access_key=school_access_key)
    template = loader.get_template("view_timetables/selection_dashboard.html")
    return HttpResponse(template.render(context, request))


@login_required
def pupil_navigator(request) -> HttpResponse:
    """
    View to provide a list of pupils which the user can navigate to view/retrieve each of their timetables.
    This is pre-processed to be indexed by year group for display in the template.
    """
    school_id = request.user.profile.school.school_access_key
    year_indexed_pupils = view_timetables.get_year_indexed_pupils(school_id=school_id)
    template = loader.get_template("view_timetables/pupils_navigator.html")
    context = {
        "all_pupils": year_indexed_pupils
    }
    return HttpResponse(template.render(context, request))


@login_required
def teacher_navigator(request) -> HttpResponse:
    """
    View to provide a list of teachers which the user can navigate to view/retrieve each of their timetables.
    Pre-processed to return a dictionary of teachers with the surnames indexed alphabetically.
    """
    school_id = request.user.profile.school.school_access_key
    all_teachers = view_timetables.get_letter_indexed_teachers(school_id=school_id)
    template = loader.get_template("view_timetables/teachers_navigator.html")
    context = {
        "all_teachers": all_teachers
    }
    return HttpResponse(template.render(context, request))


@login_required
def pupil_timetable(request, id: int) -> HttpResponse:
    """View for rendering the timetable of the individual pupil with the passed id, with context from domain layer."""
    school_id = request.user.profile.school.school_access_key
    pupil, timetable, timetable_colours = view_timetables.get_pupil_timetable_context(pupil_id=id, school_id=school_id)

    template = loader.get_template("view_timetables/pupil_timetable.html")
    context = {
        "pupil": pupil,
        "timetable": timetable,
        "class_colours": timetable_colours,
    }
    return HttpResponse(template.render(context, request))


@login_required
def teacher_timetable(request, id: int) -> HttpResponse:
    """View for the timetable of the individual teacher with the passed id."""
    school_id = request.user.profile.school.school_access_key
    teacher, timetable, year_group_colours = view_timetables.get_teacher_timetable_context(
        teacher_id=id, school_id=school_id)

    template = loader.get_template("view_timetables/teacher_timetable.html")
    context = {
        "teacher": teacher,
        "timetable": timetable,
        "year_group_colours": year_group_colours,
    }
    return HttpResponse(template.render(context, request))
