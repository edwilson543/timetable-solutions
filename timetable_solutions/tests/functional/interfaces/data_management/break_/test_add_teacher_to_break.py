"""
Tests for the related teacher table on the break update view.
"""

# Standard library imports
from collections import OrderedDict

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional import client


class TestBreakUpdateRelatedTeachersPartialAdd(client.TestClient):
    def test_loads_related_teachers_and_can_add_a_new_one_to_break(self):
        school = self.create_school_and_authorise_client()

        # Make a break that already has one teacher
        teacher = data_factories.Teacher(school=school, teacher_id=1)
        break_ = data_factories.Break(school=school, teachers=(teacher,))

        # Make another teacher, who will be second in the queryset
        other_teacher = data_factories.Teacher(school=school, teacher_id=2)

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
                    ("timetable_url", ""),
                ]
            )
        ]

        # Check there are no errors on the django form and the right teachers are shown
        django_form = response.context["add_form"]
        assert not django_form.errors
        assert django_form.fields["teacher"].queryset.get() == other_teacher

        # Select a teacher to add from the add form
        webtest_form = response.forms["teachers-add-form"]
        webtest_form["teacher"] = other_teacher.pk
        response = self.hx_post_form(webtest_form)

        # Check the response and that the other teacher is now in the list
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
                    ("timetable_url", ""),
                ]
            ),
            OrderedDict(
                [
                    ("teacher_id", other_teacher.teacher_id),
                    ("firstname", other_teacher.firstname),
                    ("surname", other_teacher.surname),
                    ("title", other_teacher.title),
                    (
                        "update_url",
                        UrlName.TEACHER_UPDATE.url(teacher_id=other_teacher.teacher_id),
                    ),
                    ("timetable_url", ""),
                ]
            ),
        ]

        # The form should now be disabled since there are no more teachers to add
        django_form = response.context["add_form"]
        assert django_form.fields["teacher"].disabled

    def test_cannot_add_teacher_that_would_lead_to_a_clash(self):
        school = self.create_school_and_authorise_client()

        # Make a break that already has one teacher
        teacher = data_factories.Teacher(school=school)
        break_ = data_factories.Break(school=school, teachers=(teacher,))

        # Make a break at the same time that we will try adding the teacher to
        other_break = data_factories.Break(
            school=school,
            starts_at=break_.starts_at,
            ends_at=break_.ends_at,
            day_of_week=break_.day_of_week,
        )

        # Get the related teachers partial for the other break
        url = UrlName.BREAK_ADD_TEACHERS_PARTIAL.url(break_id=other_break.break_id)
        response = self.hx_get(url)

        assert response.status_code == 200

        # Fill out the form, trying to add the teacher to the break at the same time
        webtest_form = response.forms["teachers-add-form"]
        webtest_form["teacher"] = teacher.pk
        response = self.hx_post_form(webtest_form)

        # Check the response and that the operation was unsuccessful
        assert response.status_code == 200

        django_form = response.context["add_form"]
        assert django_form.errors

        # The other break should still have no teachers assigned
        assert not response.context["page_obj"].object_list
