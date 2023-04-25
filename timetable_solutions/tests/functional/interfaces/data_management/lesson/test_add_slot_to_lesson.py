"""
Tests for the related user defined slot table on the lesson update view.
"""

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional import client


class TestLessonUpdateUserDefinedTimetableSlotPartial(client.TestClient):
    def test_loads_related_slots_and_can_add_pupil_to_lesson(self):
        school = self.create_school_and_authorise_client()

        # Make a lesson with a user defined slot
        slot = data_factories.TimetableSlot(school=school)
        lesson = data_factories.Lesson(school=school, user_defined_time_slots=(slot,))

        # Make another pupil, who will be second in the queryset
        other_slot = data_factories.TimetableSlot(school=school)

        # Get the related slots partial
        url = UrlName.LESSON_UPDATE_USER_SLOTS_PARTIAL.url(lesson_id=lesson.lesson_id)
        response = self.hx_get(url)

        # Ensure response ok and the correct context was loaded
        assert response.status_code == 200
        assert len(response.context["page_obj"].object_list) == 1

        # Check there are no errors on the django form and the right pupils are shown
        django_form = response.context["add_form"]
        assert not django_form.errors
        assert django_form.fields["slot"].queryset.get() == other_slot

        # Select a pupil to add from the add form
        webtest_form = response.forms["user_defined_time_slots-add-form"]
        webtest_form["slot"] = other_slot.pk
        response = self.hx_post_form(webtest_form)

        # Check the response and that the other pupil is now in the list
        assert response.status_code == 200

        assert len(response.context["page_obj"].object_list) == 2
        assert lesson.user_defined_time_slots.count() == 2

        # The form should now be disabled since there are no more slots to add
        django_form = response.context["add_form"]
        assert django_form.fields["slot"].disabled

    def test_cannot_add_slot_that_would_lead_to_a_clash(self):
        school = self.create_school_and_authorise_client()

        # Make a pupil that is already busy for some slot
        pupil = data_factories.Pupil(school=school)
        slot = data_factories.TimetableSlot(school=school)
        data_factories.Lesson(
            school=school, pupils=(pupil,), user_defined_time_slots=(slot,)
        )

        # Make a lesson at the same time that we will try adding the slot to
        other_lesson = data_factories.Lesson(school=school, pupils=(pupil,))

        # Get the related pupils partial for the other lesson
        url = UrlName.LESSON_UPDATE_USER_SLOTS_PARTIAL.url(
            lesson_id=other_lesson.lesson_id
        )
        response = self.hx_get(url)

        assert response.status_code == 200

        # Fill out the form, trying to add the slot to the lesson at the same time
        webtest_form = response.forms["user_defined_time_slots-add-form"]
        webtest_form["slot"] = slot.pk
        response = self.hx_post_form(webtest_form)

        # Check the response and that the operation was unsuccessful
        assert response.status_code == 200

        django_form = response.context["add_form"]
        assert django_form.errors

        # The other lesson should still have no slots assigned
        assert not response.context["page_obj"].object_list
