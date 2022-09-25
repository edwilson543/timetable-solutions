"""Unit tests for the TimetableSolverInputs class"""

# Django imports
from django import test

# Local application imports
from data import models
from domain.solver.constants import school_dataclasses
from domain.solver import linear_programming as lp


class TestTimetableSolverInputsLoading(test.LiveServerTestCase):
    """
    Note that we use the LiveServerTestCase since the solver is effectively (designed to be possible to be) outside of
    this repository and thus uses the requests module to POST to the REST API.
    Therefore we need a full url to pass to requests.post()
    """

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json"]
    # We need the fixtures since we're posting fixed class instances related to other database tables

    def test_post_results_valid_fixed_class_data(self):
        """
        Test that the extracted FixedClass data can be posted back to the main django project's databse via the
        REST API

        db fixture is a pytest-django default fixture representing the test database
        """
        # Set test parameters
        fc1 = school_dataclasses.FixedClass(school=123456, class_id="A", teacher=1, pupils=[1, 2], classroom=1,
                                            time_slots=[1, 2], subject_name="MATHS", user_defined=False)
        fc2 = school_dataclasses.FixedClass(school=123456, class_id="B", teacher=2, pupils=[3, 4], classroom=2,
                                            time_slots=[3, 4], subject_name="ENGLISH", user_defined=False)
        fixed_class_data = [fc1, fc2]

        # noinspection PyTypeChecker
        outcome = lp.TimetableSolverOutcome(timetable_solver=None)
        outcome.solver_fixed_class_data = fixed_class_data

        school_access_key = 123456
        url = f"{self.live_server_url}/api/fixedclasses/?school_access_key={school_access_key}"

        # Execute the test unit
        response = outcome._post_results(url=url)

        # Check the outcome
        assert response.status_code == 201
        fc1 = models.FixedClass.objects.get_individual_fixed_class(school_id=123456, class_id="A")
        assert isinstance(fc1, models.FixedClass)
        fc2 = models.FixedClass.objects.get_individual_fixed_class(school_id=123456, class_id="B")
        assert isinstance(fc2, models.FixedClass)
