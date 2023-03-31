"""
Unit tests for the views in the create_timetable app
"""


# Standard library imports
import datetime as dt

# Django imports
from django import test, urls
from django.contrib.auth.models import User

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
