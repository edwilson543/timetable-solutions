# Django imports
from django import test
from django import urls

# Local application imports
from interfaces.create_timetables import forms


class TestCreateTimetableFormView(test.TestCase):
    """
    Class for unit tests of the view allowing users to create timetable solutions.
    """
    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes_lunch.json", "unsolved_classes.json"]

    def test_get_method_returns_empty_solution_specification_form(self):
        """Test that by submitting GET request to the create timetable url,"""
        # Set test parameters
        self.client.login(username="dummyteacher", password="dt123dt123")
        url = urls.reverse("create_timetables")

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        assert response.status_code == 200
        assert isinstance(response.context["form"], forms.SolutionSpecification)

    # TODO - combine the class with django.contrib.auth.mixins LoginRequiredMixin and test
