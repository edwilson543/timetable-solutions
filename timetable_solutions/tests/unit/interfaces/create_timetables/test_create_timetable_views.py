"""
Unit tests for the views in the create_timetable app
"""

# Standard library imports
import datetime as dt

# Django imports
from django import test
from django.contrib.auth.models import User
from django import urls

# Local application imports
from interfaces.constants import UrlName
from interfaces.create_timetables import views


class TestCreateTimetableFormView(test.TestCase):
    """
    Class for Unit tests of the CreateTimetable FormView allowing users to create timetable solutions.
    """

    fixtures = ["user_school_profile.json", "year_groups.json", "timetable.json"]

    def test_get_form_kwargs_contains_correct_available_time_slots(self):
        """
        Unit test for the method over-riding FormView's get_form_kwargs method
        """
        # Set test parameters
        factory = test.RequestFactory()
        request = factory.get(urls.reverse(UrlName.CREATE_TIMETABLES.value))
        request.user = User.objects.get(pk=1)  # Dummy teacher has pk=1
        view = views.CreateTimetable(request=request)

        # Execute test unit
        kwargs = view.get_form_kwargs()

        # Check outcome
        available_slots = kwargs["available_time_slots"]
        assert available_slots == [
            dt.time(hour=hour) for hour in range(9, 13)
        ] + [  # Lunch break (note that 13-14 isn't include since range s right-open)
            dt.time(hour=hour) for hour in range(14, 16)
        ]

    def test_get_context_dictionary_ready_to_create_false_as_fixtures_are_sparse(self):
        """
        Unit test for the method over-riding FormMixin's get_context_data method.
        Note that this TestCase uses insufficient fixtures to fully define the timetabling problem (analogous to the
        user having uploaded insufficient data), and therefore we expect the ready_to_create variable to be False.
        """
        # Set test parameters
        factory = test.RequestFactory()
        request = factory.get(urls.reverse(UrlName.CREATE_TIMETABLES.value))
        request.user = User.objects.get(pk=1)  # Dummy teacher has pk=1
        view = views.CreateTimetable(request=request)

        # Execute test unit
        context_dict = view.get_context_data()

        # Check outcome
        ready_to_create = context_dict["ready_to_create"]
        assert not ready_to_create
