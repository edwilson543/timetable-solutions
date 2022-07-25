# Django imports
from django.http import HttpResponse
from django.template import loader


def selection_navigator(request):
    """View to bring up the main navigation screen for guiding the user towards individual timetables."""
    template = loader.get_template("selection_navigator.html")
    return HttpResponse(template.render({}, request))


def teacher_navigator(request):
    """View to bring up a list of teachers which can be linked out to each of their timetables."""
    pass

def pupil_navigator(request):
    """View to bring up a list of pupils which can be linked out to each of their timetables."""
    template = loader.get_template("pupils_navigator.html")
    return HttpResponse(template.render({}, request))
