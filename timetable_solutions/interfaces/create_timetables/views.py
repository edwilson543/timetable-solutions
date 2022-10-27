"""
Module containing the view class for the timetable creation page.
"""

# Standard library imports
from typing import List, Dict

# Django imports
from django import urls
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic.edit import FormView

# Local application imports
from constants.url_names import UrlName
from domain.data_upload_processing import get_upload_status
from domain import solver
from domain import utils as domain_utils
from interfaces.create_timetables import forms


class CreateTimetable(LoginRequiredMixin, FormView):
    """
    View relating to the 'dashboard' / homepage of the 'create' component on the wider application, which allows
    users to initiate the creation of timetable solutions.

    We use a FormView since this is simply an exercise in taking the user's form data and using it to initiate some
    processing.
    Note also that we use reverse_lazy since a URL reversal is needed BEFORE the URLConf is loaded, to avoid circular
    imports.
    """
    # LoginRequiredMixin attributes
    login_url = urls.reverse_lazy(UrlName.LOGIN.value)

    # FormView attributes
    form_class = forms.SolutionSpecification
    template_name = "create_timetables.html"
    success_url = urls.reverse_lazy(UrlName.VIEW_TIMETABLES_DASH.value)

    def form_valid(self, form) -> HttpResponse:
        """
        Method to take the user's requirements as per the form, and then use them to run the solver.
        This will either redirect the user to the viewing dashboard, or it will flash the error messages.
        """
        error_messages = self._run_solver_from_view(form=form)
        if len(error_messages) == 0:
            return super().form_valid(form)  # Method inherited from ModelFormMixin
        else:
            context_data = self.get_context_data()
            context_data["error_messages"] = error_messages
            return super().render_to_response(context=context_data)  # from views.generic.base.TemplateResponseMixin

    def _run_solver_from_view(self, form) -> List[str]:
        """
        Method to run the solver at the point when the user submits their form.
        :return - error_messages - the list of error messages encountered by the solver (hopefully will have length 0).
        """
        school_access_key = self.request.user.profile.school.school_access_key
        solution_spec = form.get_solution_specification_from_form_data()
        error_messages = solver.produce_timetable_solutions(
            school_access_key=school_access_key, solution_specification=solution_spec)
        return error_messages

    # METHODS OVERRIDING SUPERCLASS METHODS
    def get_context_data(self, **kwargs) -> Dict:
        """
        Method adding additional context to the context dictionary provided by super class.
        In particular, we need to carry a boolean that's True if the user has uploaded all data and can start creating
        timetables, and False if they need to complete the data upload step.
        """
        context_data = super().get_context_data()  # Method inherited from views.generic.edit.FormMixin
        upload_status = get_upload_status(school=self.request.user.profile.school)
        ready_to_create: bool = (
                upload_status.PUPILS * upload_status.TEACHERS * upload_status.TIMETABLE *
                upload_status.CLASSROOMS * upload_status.UNSOLVED_CLASSES * upload_status.FIXED_CLASSES)
        context_data["ready_to_create"] = ready_to_create
        return context_data

    def get_form_kwargs(self) -> Dict:
        """
        Method used to add kwargs during the form's initialisation.
        Specifically we add available_time_slots, which get added to the choices for one of the form fields in __init__
        """
        kwargs = super().get_form_kwargs()
        school_access_key = self.request.user.profile.school.school_access_key

        timeslots = domain_utils.get_user_timetable_slots(school_access_key=school_access_key)
        kwargs["available_time_slots"] = timeslots
        return kwargs
