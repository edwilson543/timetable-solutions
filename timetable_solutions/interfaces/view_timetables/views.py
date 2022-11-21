"""Views used to navigate users towards an individual pupil/teacher's timetable."""

# Standard library imports
import io

# Third party imports
from xhtml2pdf import pisa

# Django imports
from django.contrib.auth.decorators import login_required
from django import http
from django.template import loader

# Local application imports
from domain import view_timetables


@login_required
def selection_dashboard(request: http.HttpRequest) -> http.HttpResponse:
    """View providing the context for the information displayed on the selection dashboard"""
    school_access_key = request.user.profile.school.school_access_key
    context = view_timetables.timetable_summary_stats.get_summary_stats_for_dashboard(
        school_access_key=school_access_key)
    template = loader.get_template("view_timetables/selection_dashboard.html")
    return http.HttpResponse(template.render(context, request))


@login_required
def pupil_navigator(request: http.HttpRequest) -> http.HttpResponse:
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
    return http.HttpResponse(template.render(context, request))


@login_required
def teacher_navigator(request: http.HttpRequest) -> http.HttpResponse:
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
    return http.HttpResponse(template.render(context, request))


@login_required
def pupil_timetable(request: http.HttpRequest, pupil_id: int) -> http.HttpResponse:
    """
    View for rendering the timetable of the individual pupil with the passed id.
    Note that the pupil_id is unique together with the school access key,
    and so different users will see different content at the requested url.
    """
    school_id = request.user.profile.school.school_access_key
    pupil, timetable, timetable_colours = view_timetables.get_pupil_timetable_context(
        pupil_id=pupil_id, school_id=school_id)

    template = loader.get_template("view_timetables/pupil_timetable.html")
    context = {
        "pupil": pupil,
        "timetable": timetable,
        "class_colours": timetable_colours,
    }
    return http.HttpResponse(template.render(context, request))


@login_required
def teacher_timetable(request: http.HttpRequest, teacher_id: int) -> http.HttpResponse:
    """
    View for the timetable of the individual teacher with the passed id.
    Note that the teacher_id is unique together with the school access key,
    and so different users will see different content at the requested url.
    """
    school_id = request.user.profile.school.school_access_key
    teacher, timetable, year_group_colours = view_timetables.get_teacher_timetable_context(
        teacher_id=teacher_id, school_id=school_id)

    template = loader.get_template("view_timetables/teacher_timetable.html")
    context = {
        "teacher": teacher,
        "timetable": timetable,
        "year_group_colours": year_group_colours,
    }
    return http.HttpResponse(template.render(context, request))


@login_required
def pupil_timetable_download_csv(request: http.HttpRequest, pupil_id: int) -> http.HttpResponse:
    """
    View used to serve an individual pupil timetable as a csv file download.
    :return - a http response with a csv file attachment
    """
    school_id = request.user.profile.school.school_access_key
    pupil, csv_buffer = view_timetables.get_pupil_timetable_as_csv(school_id=school_id, pupil_id=pupil_id)
    filename = f"Timetable-{pupil.firstname}-{pupil.surname}.csv"

    response = http.HttpResponse(csv_buffer, content_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename={filename}",
    })
    return response


@login_required
def teacher_timetable_download_csv(request: http.HttpRequest, teacher_id: int) -> http.HttpResponse:
    """
    View used to serve an individual teacher timetable as a csv file download.
    :return - a http response with a csv file attachment
    """
    school_id = request.user.profile.school.school_access_key
    teacher, csv_buffer = view_timetables.get_teacher_timetable_as_csv(school_id=school_id, teacher_id=teacher_id)
    filename = f"Timetable-{teacher.firstname}-{teacher.surname}.csv"

    response = http.HttpResponse(csv_buffer, content_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename={filename}",
    })
    return response


@login_required
def pupil_timetable_download_pdf(request: http.HttpRequest, pupil_id: int) -> http.HttpResponse:
    """
    View used to serve an individual pupil timetable as a csv file download.
    :return - a http response with a csv file attachment
    """
    # Get the html template
    school_id = request.user.profile.school.school_access_key
    pupil, timetable, timetable_colours = view_timetables.get_pupil_timetable_context(
        pupil_id=pupil_id, school_id=school_id)
    template = loader.get_template("view_timetables/pdfs/pupil_timetable.html")
    context = {"pupil": pupil, "timetable": timetable, "class_colours": timetable_colours}
    html = template.render(context)

    # Create the pdf and add it as a file download
    pdf_buffer = io.BytesIO()
    pisa.pisaDocument(src=html, dest=pdf_buffer)
    pdf_buffer.seek(0)
    filename = f"Timetable-{pupil.firstname}-{pupil.surname}.pdf"
    response = http.HttpResponse(pdf_buffer, content_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename={filename}"})

    return response


@login_required
def teacher_timetable_download_pdf(request: http.HttpRequest, teacher_id: int) -> http.HttpResponse:
    """
    View used to serve an individual pupil timetable as a csv file download.
    :return - a http response with a csv file attachment
    """
    # Get the html template
    school_id = request.user.profile.school.school_access_key
    teacher, timetable, year_group_colours = view_timetables.get_teacher_timetable_context(
        teacher_id=teacher_id, school_id=school_id)
    template = loader.get_template("view_timetables/pdfs/teacher_timetable.html")
    context = {"teacher": teacher, "timetable": timetable, "year_group_colours": year_group_colours}
    html = template.render(context)

    # Create the pdf and add it as a file download
    pdf_buffer = io.BytesIO()
    pisa.pisaDocument(src=html, dest=pdf_buffer)
    pdf_buffer.seek(0)
    filename = f"Timetable-{teacher.firstname}-{teacher.surname}.pdf"
    response = http.HttpResponse(pdf_buffer, content_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename={filename}"})

    return response
