"""
Integration tests for the views in the create_timetable app
"""

# Standard library imports
import datetime as dt

# Django imports
from django import test
from django import urls

# Local application imports
from constants.url_names import UrlName
from data import models
from domain.solver import SolutionSpecification
from interfaces.create_timetables import forms


class TestCreateTimetableFormView(test.TestCase):
    """
    Class for integration tests of the CreateTimetable FormView allowing users to create timetable solutions.
    'Integration' since all tests involve fully running the solver.
    """

    fixtures = [
        "user_school_profile.json",
        "teachers.json",
        "classrooms.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
        "lessons_without_solution.json",
    ]

    # GET request tests
    def test_get_method_returns_empty_solution_specification_form(self):
        """
        Test that by submitting GET request to the create timetable url, the empty SolutionSpecification form is
        rendered.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = urls.reverse(UrlName.CREATE_TIMETABLES.value)

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        assert response.status_code == 200
        assert isinstance(response.context["form"], forms.SolutionSpecification)

    def test_get_method_redirects_to_login_for_logged_out_user(self):
        """
        Test that submitting a GET request to the create timetable page when not logged in just redirects the user.
        """
        # Set test parameters
        url = urls.reverse(UrlName.CREATE_TIMETABLES.value)
        expected_redirect_url = urls.reverse(UrlName.LOGIN.value) + "?next=/create/"

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        self.assertIn(expected_redirect_url, response.url)

    # POST request tests
    def _post_form_data_to_url_and_test_outcome(self, form_data: dict):
        """
        Utility test method that posts the passed form_data to the create_timetable URL, and checks whether the solver
        has been executed as appropriate.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = urls.reverse(UrlName.CREATE_TIMETABLES.value)
        expected_url_redirect = urls.reverse(UrlName.VIEW_TIMETABLES_DASH.value)

        # Execute test unit
        response = self.client.post(url, data=form_data)

        # Check the response redirects
        assert response.headers["HX-Redirect"] == expected_url_redirect

        # Check that a solution has been produced
        lessons = models.Lesson.objects.get_all_instances_for_school(school_id=123456)
        for lesson in lessons:
            if lesson.requires_solving():
                assert lesson.solver_defined_time_slots.count() in [
                    8,
                    9,
                ]  # per requirements

    def test_post_method_runs_solver_with_solution_spec_form_using_simplest_run_options(
        self,
    ):
        """
        Test that by submitting a POST request to the create timetable url, with a SolutionSpecification form that uses
        simple run requirements (i.e. allows all simplifications), the solver is run successfully.
        """
        form_data = {
            "allow_split_classes_within_each_day": True,
            "allow_triple_periods_and_above": True,
            "optimal_free_period_time_of_day": SolutionSpecification.OptimalFreePeriodOptions.NONE,
            "ideal_proportion_of_free_periods_at_this_time": 1.0,
        }
        self._post_form_data_to_url_and_test_outcome(form_data=form_data)

    def test_post_method_runs_solver_with_solution_spec_form_disallow_everything(self):
        """
        Test that by submitting a POST request to the create timetable url, with a SolutionSpecification form that
        forces all components (i.e. constraints / objective) of the solver to be used, the solver is run successfully.
        """
        form_data = {
            "allow_split_classes_within_each_day": False,  # Note these are set to False
            "allow_triple_periods_and_above": False,
            "optimal_free_period_time_of_day": SolutionSpecification.OptimalFreePeriodOptions.NONE,
            "ideal_proportion_of_free_periods_at_this_time": 0.70,
        }
        self._post_form_data_to_url_and_test_outcome(form_data=form_data)

    def test_post_method_runs_solver_with_solution_spec_form_disallow_everything_specify_optimal_time_exact(
        self,
    ):
        """
        Test that by submitting a POST request to the create timetable url, with a SolutionSpecification form that
        includes an specific optimal free period time and ideal proportion, the solver runs as expected
        """
        form_data = {
            "allow_split_classes_within_each_day": False,  # Note these are set to False
            "allow_triple_periods_and_above": False,
            "optimal_free_period_time_of_day": dt.time(hour=9),
            "ideal_proportion_of_free_periods_at_this_time": 0.5,
        }
        self._post_form_data_to_url_and_test_outcome(form_data=form_data)

    def test_post_method_runs_solver_with_solution_spec_form_disallow_everything_specify_optimal_time_morning(
        self,
    ):
        """
        Test that by submitting a POST request to the create timetable url, with a SolutionSpecification form that
        includes an optimum free period specified as the MORNING, and an ideal proportion, the solver runs as expected
        """
        form_data = {
            "allow_split_classes_within_each_day": False,  # Note these are set to False
            "allow_triple_periods_and_above": False,
            "optimal_free_period_time_of_day": SolutionSpecification.OptimalFreePeriodOptions.MORNING,
            "ideal_proportion_of_free_periods_at_this_time": 0.5,
        }
        self._post_form_data_to_url_and_test_outcome(form_data=form_data)

    def test_post_method_runs_solver_with_solution_spec_form_disallow_everything_specify_optimal_time_afternoon(
        self,
    ):
        """
        Test that by submitting a POST request to the create timetable url, with a SolutionSpecification form that
        includes an optimum free period specified as the AFTERNOON, and an ideal proportion, the solver runs as expected
        """
        form_data = {
            "allow_split_classes_within_each_day": False,  # Note these are set to False
            "allow_triple_periods_and_above": False,
            "optimal_free_period_time_of_day": SolutionSpecification.OptimalFreePeriodOptions.AFTERNOON,
            "ideal_proportion_of_free_periods_at_this_time": 0.5,
        }
        self._post_form_data_to_url_and_test_outcome(form_data=form_data)
