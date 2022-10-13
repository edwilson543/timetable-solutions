
# Django imports
from django import views
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django import urls

# Local application imports
from domain.solver.run_solver import produce_timetable_solutions
from interfaces.create_timetables import forms


class CreateTimetable(views.View):
    """
    View relating to the 'dashboard' / homepage of the 'create' component on the wider application, which allows
    users to initiate the creation of timetable solutions.
    """
    @staticmethod
    def get(request, *args, **kwargs):
        template = loader.get_template("create_timetables.html")
        context = {
            "form": forms.SolutionSpecification()
        }
        return HttpResponse(template.render(context, request))

    def post(self, request, *args, **kwargs):
        """This post method is used to initiate the running of the solver - the core service of the app."""
        form = forms.SolutionSpecification(request.POST)
        if form.is_valid():
            school_access_key = request.user.profile.school.school_access_key
            produce_timetable_solutions(school_access_key=school_access_key)
            return HttpResponseRedirect(urls.reverse("selection_dashboard"))
        else:
            return self.get(request, *args, **kwargs)
