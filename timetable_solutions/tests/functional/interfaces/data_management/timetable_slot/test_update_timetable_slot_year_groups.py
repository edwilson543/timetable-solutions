"""
Tests for updating a timetable slot's relevant year groups via the TimetableSlotUpdate view.
"""

# Local application imports
from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers import webtest_forms


class TestTimetableSlotUpdate(TestClient):
    def test_can_add_year_group_to_a_slots_relevant_year_groups(self):
        # Authorise the client for some school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Make a slot's data to access, with one relevant year group at present
        yg = data_factories.YearGroup(school=school)
        slot = data_factories.TimetableSlot(school=school, relevant_year_groups=(yg,))
        # And another year group to make relevant
        other_yg = data_factories.YearGroup(school=school)

        # Navigate to this slot's detail view
        url = UrlName.TIMETABLE_SLOT_UPDATE.url(slot_id=slot.slot_id)
        page = self.client.get(url)

        # Check response ok and correct initials set in the update year groups form
        assert page.status_code == 200

        # Fill out the form by selecting both year groups as relevant to the slot
        form = page.forms["update-year-groups-form"]
        selection = [str(yg.pk), str(other_yg.pk)]
        webtest_forms.select_multiple(
            form, field_name="relevant_year_groups", selection=selection
        )
        response = form.submit(name="update-year-groups-submit")

        assert response.status_code == 302

        # Ensure the slot's relevant year groups was updated to the selection
        slot.refresh_from_db()
        all_ygs = models.YearGroup.objects.all()
        assert (slot.relevant_year_groups.all() & all_ygs).count() == all_ygs.count()

    def test_can_remove_a_year_group_from_a_slots_relevant_year_groups(self):
        # Authorise the client for some school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Make a slot's data to access, with two relevant year groups
        yg = data_factories.YearGroup(school=school)
        other_yg = data_factories.YearGroup(school=school)
        slot = data_factories.TimetableSlot(
            school=school, relevant_year_groups=(yg, other_yg)
        )

        # Navigate to this slot's detail view
        url = UrlName.TIMETABLE_SLOT_UPDATE.url(slot_id=slot.slot_id)
        page = self.client.get(url)

        # Check response ok and correct initials set in the update year groups form
        assert page.status_code == 200

        # Fill out the form by removing other_yg from the relevant slots
        form = page.forms["update-year-groups-form"]
        selection = [str(yg.pk)]
        webtest_forms.select_multiple(
            form, field_name="relevant_year_groups", selection=selection
        )
        response = form.submit(name="update-year-groups-submit")

        assert response.status_code == 302

        # Ensure the slot's relevant year groups was updated to the selection
        slot.refresh_from_db()
        assert slot.relevant_year_groups.get() == yg

    def test_cannot_make_slot_relevant_to_a_year_group_leading_to_a_clash(self):
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Make a slot for some year group
        yg = data_factories.YearGroup(school=school)
        slot = data_factories.TimetableSlot(
            school=school,
            relevant_year_groups=(yg,),
        )
        # Make another year group with a slot at the same time
        other_yg = data_factories.YearGroup(school=school)
        data_factories.TimetableSlot(
            school=school,
            relevant_year_groups=(other_yg,),
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            day_of_week=slot.day_of_week,
        )

        # Navigate to this slot's detail view
        url = UrlName.TIMETABLE_SLOT_UPDATE.url(slot_id=slot.slot_id)
        page = self.client.get(url)

        # Check response ok and correct initials set in the update year groups form
        assert page.status_code == 200

        # Try making the first slot relevant to the other year group
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

        slot.refresh_from_db()
        assert slot.relevant_year_groups.get() == yg
