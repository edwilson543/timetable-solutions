"""
Tests for removing a related teacher from a break.
"""

# Standard library imports
from collections import OrderedDict

# Django imports
from django import test

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional import client


class TestBreakUpdateRelatedTeachersPartialRemove(client.TestClient):
    @test.override_settings(DEBUG=True)
    def test_loads_related_teachers_and_then_can_remove_one(self):
        school = self.create_school_and_authorise_client()

        # Make a break with two teachers
        teacher = data_factories.Teacher(school=school, teacher_id=1)
        remove_teacher = data_factories.Teacher(school=school, teacher_id=2)
        break_ = data_factories.Break(school=school, teachers=(teacher, remove_teacher))

        # Get the related teachers partial
        url = UrlName.BREAK_ADD_TEACHERS_PARTIAL.url(break_id=break_.break_id)
        response = self.hx_get(url)

        # Ensure response ok and the correct context was loaded
        assert response.status_code == 200
        assert response.context["page_obj"].object_list == [
            OrderedDict(
                [
                    ("teacher_id", teacher.teacher_id),
                    ("firstname", teacher.firstname),
                    ("surname", teacher.surname),
                    ("title", teacher.title),
                    (
                        "update_url",
                        UrlName.TEACHER_UPDATE.url(teacher_id=teacher.teacher_id),
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("teacher_id", remove_teacher.teacher_id),
                    ("firstname", remove_teacher.firstname),
                    ("surname", remove_teacher.surname),
                    ("title", remove_teacher.title),
                    (
                        "update_url",
                        UrlName.TEACHER_UPDATE.url(
                            teacher_id=remove_teacher.teacher_id
                        ),
                    ),
                ]
            ),
        ]

        # The form should be disabled since there are no teachers to add
        django_form = response.context["add_form"]
        assert django_form.fields["teacher"].disabled

        # Get one of the teacher remove forms
        webtest_form = response.forms[
            f"teachers-remove-form-{remove_teacher.teacher_id}"
        ]
        response = self.hx_delete_form(url, form=webtest_form)

        # Check the response and that only one of the teachers is now in the table
        assert response.status_code == 200

        assert response.context["page_obj"].object_list == [
            OrderedDict(
                [
                    ("teacher_id", teacher.teacher_id),
                    ("firstname", teacher.firstname),
                    ("surname", teacher.surname),
                    ("title", teacher.title),
                    (
                        "update_url",
                        UrlName.TEACHER_UPDATE.url(teacher_id=teacher.teacher_id),
                    ),
                ]
            )
        ]

        # The form should now have the remove teacher as a choice to add to the break
        django_form = response.context["add_form"]
        assert django_form.fields["teacher"].queryset.get() == remove_teacher
