"""
Tests for removing a pupil from a lesson.
"""

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional import client


class TestLessonUpdatePupilsPartialRemove(client.TestClient):
    def test_loads_related_pupils_and_then_can_remove_one(self):
        school = self.create_school_and_authorise_client()

        # Make a lesson that has one pupil
        remove_pupil = data_factories.Pupil(school=school)
        lesson = data_factories.Lesson(school=school, pupils=(remove_pupil,))

        # Get the related pupils partial
        url = UrlName.LESSON_UPDATE_PUPILS_PARTIAL.url(lesson_id=lesson.lesson_id)
        response = self.hx_get(url)

        # The add form should be disabled since there are no pupils to add
        django_form = response.context["add_form"]
        assert django_form.fields["pupil"].disabled

        # Get one of the pupil remove forms
        webtest_form = response.forms[f"pupils-remove-form-{remove_pupil.pupil_id}"]
        response = self.hx_delete_form(url, form=webtest_form)

        # Check the response and that only one of the pupils is now in the table
        assert response.status_code == 200

        assert len(response.context["page_obj"].object_list) == 0

        # The form should now have the remove pupil as a choice to add to the break
        django_form = response.context["add_form"]
        assert django_form.fields["pupil"].queryset.get() == remove_pupil
