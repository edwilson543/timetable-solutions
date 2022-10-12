
# Django imports
from django.http import HttpResponse
from django import views
from django.template import loader

# Local application imports
from interfaces.create_timetables import forms


class CreateTimetable(views.View):
    """
    View relating to the 'dashboard' / homepage of the 'create' component on the wider application, which allows
    users to initiate the creation of timetable solutions.
    """
    @staticmethod
    def get(request, *args, **kwargs):
        template = loader.get_template("create")
        context = {
            "form": forms.SolutionSpecification()
        }
        return HttpResponse(template.render(context, request))

    def post(self, request, *args, **kwargs):
        pass
