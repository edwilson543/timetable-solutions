"""
Tests for updating a break's relevant year groups via the BreakUpdate view.
"""

# Local application imports
from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers import webtest_forms


class TestBreakUpdate(TestClient):
    def test_can_add_year_group_to_a_breaks_relevant_year_groups(self):
        # Authorise the client for some school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Make a break_'s data to access, with one relevant year group at present
        yg = data_factories.YearGroup(school=school)
        break_ = data_factories.Break(school=school, relevant_year_groups=(yg,))
        # And another year group to make relevant
        other_yg = data_factories.YearGroup(school=school)

        # Navigate to this break_'s detail view
        url = UrlName.BREAK_UPDATE.url(break_id=break_.break_id)
        page = self.client.get(url)

        # Check response ok and correct initials set in the update year groups form
        assert page.status_code == 200

        # Fill out the form by selecting both year groups as relevant to the break_
        form = page.forms["update-year-groups-form"]
        selection = [str(yg.pk), str(other_yg.pk)]
        webtest_forms.select_multiple(
            form, field_name="relevant_year_groups", selection=selection
        )
        response = form.submit(name="update-year-groups-submit")

        assert response.status_code == 302

        # Ensure the break_'s relevant year groups was updated to the selection
        break_.refresh_from_db()
        all_ygs = models.YearGroup.objects.all()
        assert (break_.relevant_year_groups.all() & all_ygs).count() == all_ygs.count()

    def test_can_remove_a_year_group_from_a_breaks_relevant_year_groups(self):
        # Authorise the client for some school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Make a break_'s data to access, with two relevant year groups
        yg = data_factories.YearGroup(school=school)
        other_yg = data_factories.YearGroup(school=school)
        break_ = data_factories.Break(
            school=school, relevant_year_groups=(yg, other_yg)
        )

        # Navigate to this break_'s detail view
        url = UrlName.BREAK_UPDATE.url(break_id=break_.break_id)
        page = self.client.get(url)

        # Check response ok and correct initials set in the update year groups form
        assert page.status_code == 200

        # Fill out the form by removing other_yg from the relevant breaks
        form = page.forms["update-year-groups-form"]
        selection = [str(yg.pk)]
        webtest_forms.select_multiple(
            form, field_name="relevant_year_groups", selection=selection
        )
        response = form.submit(name="update-year-groups-submit")

        assert response.status_code == 302

        # Ensure the break_'s relevant year groups was updated to the selection
        break_.refresh_from_db()
        assert break_.relevant_year_groups.get() == yg

    def test_cannot_make_break_relevant_to_a_year_group_leading_to_a_clash(self):
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Make a break_ for some year group
        yg = data_factories.YearGroup(school=school)
        break_ = data_factories.Break(
            school=school,
            relevant_year_groups=(yg,),
        )
        # Make another year group with a break_ at the same time
        other_yg = data_factories.YearGroup(school=school)
        data_factories.Break(
            school=school,
            relevant_year_groups=(other_yg,),
            starts_at=break_.starts_at,
            ends_at=break_.ends_at,
            day_of_week=break_.day_of_week,
        )

        # Navigate to this break_'s detail view
        url = UrlName.BREAK_UPDATE.url(break_id=break_.break_id)
        page = self.client.get(url)

        # Check response ok and correct initials set in the update year groups form
        assert page.status_code == 200

        # Try making the first break_ relevant to the other year group
        form = page.forms["update-year-groups-form"]
        selection = [str(yg.pk), str(other_yg.pk)]
        webtest_forms.select_multiple(
            form, field_name="relevant_year_groups", selection=selection
        )
        response = form.submit(name="update-year-groups-submit")

        # Check response ok but the operation failed
        assert response.status_code == 200
        django_form = response.context["update_year_groups_form"]
        assert django_form.errors

        break_.refresh_from_db()
        assert break_.relevant_year_groups.get() == yg
