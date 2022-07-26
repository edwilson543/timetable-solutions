# Django imports
from django.http import HttpResponse
from django.template import loader

# Local application imports
from .models import Pupil


def selection_navigator(request):
    """View to bring up the main navigation screen for guiding the user towards individual timetables."""
    template = loader.get_template("selection_navigator.html")
    return HttpResponse(template.render({}, request))


def teacher_navigator(request):
    """View to bring up a list of teachers which can be linked out to each of their timetables."""
    pass


def pupil_navigator(request):
    """
    View to provide a dictionary of pupils which can be linked out to each of their timetables.
    This is pre-processed to be indexed by year group for display in the template.
    """
    year_indexed_pupils = {year: Pupil.objects.filter(year_group=year).order_by("surname").values() for
                           year in Pupil.YearGroup.values}
    year_indexed_pupils = {key: value for key, value in year_indexed_pupils.items() if len(value) > 0}
    template = loader.get_template("pupils_navigator.html")
    context = {
        "all_pupils": year_indexed_pupils
    }
    return HttpResponse(template.render(context, request))
