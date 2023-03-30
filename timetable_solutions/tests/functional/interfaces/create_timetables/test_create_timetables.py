"""
Tests for the create timetables page.
"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestCreateTimetables(TestClient):
    @pytest.mark.parametrize("optimal_free_period_time", ["MORNING", "09:00"])
    @pytest.mark.parametrize("ideal_proportion", [0.5, ""])
    def test_run_solver_with_user_specification(
        self, optimal_free_period_time: str, ideal_proportion: float | str
    ):
        school = self.create_school_and_authorise_client()

        # Create the minimum required data to have something to solve
        yg = data_factories.YearGroup(school=school)
        slot = data_factories.TimetableSlot(
            school=school, relevant_year_groups=(yg,), starts_at=dt.time(hour=9)
        )
        pupil = data_factories.Pupil(school=school, year_group=yg)
        data_factories.Break(school=school)
        lesson = data_factories.Lesson(
            school=school,
            total_required_slots=1,
            total_required_double_periods=0,
            pupils=(pupil,),
        )

        # Navigate to the crete timetables page
        url = UrlName.CREATE_TIMETABLES.url()
        page = self.client.get(url)

        assert page.status_code == 200

        # Use the form to specify some solution specification
        form = page.forms["create-timetables"]

        form["allow_split_lessons_within_each_day"] = False
        form["allow_triple_periods_and_above"] = False
        form["optimal_free_period_time_of_day"] = optimal_free_period_time
        form["ideal_proportion_of_free_periods_at_this_time"] = ideal_proportion

        response = form.submit()

        # Check response
        assert response.status_code == 302

        # Ensure the timetabling problem has actually been solved
        assert lesson.solver_defined_time_slots.get() == slot

    def test_school_with_insufficient_data_cant_access_create_timetables_form(self):
        # Create a school with no data
        self.create_school_and_authorise_client()

        # Navigate to the crete timetables page
        url = UrlName.CREATE_TIMETABLES.url()
        page = self.client.get(url)

        assert page.status_code == 200

        # Ensure they are not shown the create timetables form
        assert not page.forms.get("create-timetables")

    def test_unauthenticated_users_cannot_access_page(self):
        # Navigate to the crete timetables page
        url = UrlName.CREATE_TIMETABLES.url()
        page = self.client.get(url)

        assert page.status_code == 302
        assert "login" in page.location
