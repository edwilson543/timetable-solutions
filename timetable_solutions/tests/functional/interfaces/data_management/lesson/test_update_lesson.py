"""
Tests for updating lesson timings via the LessonUpdate view.
"""

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestLessonUpdate(TestClient):
    def test_access_detail_page_with_disabled_form(self):
        school = self.create_school_and_authorise_client()

        # Make a lesson's data to access
        yg = data_factories.YearGroup(school=school)
        lesson = data_factories.Lesson(school=school, year_group=yg)

        # Navigate to this lesson_'s detail view
        url = UrlName.LESSON_UPDATE.url(lesson_id=lesson.lesson_id)
        page = self.client.get(url)

        # Check response ok and correct context
        assert page.status_code == 200

        assert (
            page.context["serialized_model_instance"]["lesson_id"] == lesson.lesson_id
        )

        # Check the initial form values match the lesson's
        form = page.forms["disabled-update-form"]
        assert form["subject_name"].value == lesson.subject_name
        assert form["teacher"].value == str(lesson.teacher.id)
        assert form["classroom"].value == str(lesson.classroom.id)
        assert form["total_required_slots"].value == str(lesson.total_required_slots)

    def test_hx_get_enables_form_then_valid_details_submitted(self):
        school = self.create_school_and_authorise_client()

        # Make a lesson's data to access
        yg = data_factories.YearGroup(school=school)
        lesson = data_factories.Lesson(school=school, year_group=yg)

        # Navigate to this lesson's detail view
        url = UrlName.LESSON_UPDATE.url(lesson_id=lesson.lesson_id)
        form_partial = self.hx_get(url)

        # Check response ok and correct context
        assert form_partial.status_code == 200

        form = form_partial.forms["update-form"]
        assert form["subject_name"].value == lesson.subject_name
        assert form["teacher"].value == str(lesson.teacher.id)
        assert form["classroom"].value == str(lesson.classroom.id)
        assert form["total_required_slots"].value == str(lesson.total_required_slots)

        # Fill in and post the form
        form["subject_name"] = "Updated subject name"
        form["total_required_slots"] = 3
        form["total_required_double_periods"] = 1

        response = form.submit(name="update-submit")

        # Check response ok and lesson_ details updated
        assert response.status_code == 302
        assert response.location == url

        lesson.refresh_from_db()
        assert lesson.subject_name == "Updated subject name"
        assert lesson.total_required_slots == 3
        assert lesson.total_required_double_periods == 1

    def test_updating_lesson_leading_to_a_clash_for_a_teacher_fails(self):
        school = self.create_school_and_authorise_client()

        # Make a teacher busy at some slot
        yg = data_factories.YearGroup(school=school)
        teacher = data_factories.Teacher(school=school)
        slot = data_factories.TimetableSlot(school=school)
        data_factories.Lesson(
            school=school,
            year_group=yg,
            teacher=teacher,
            user_defined_time_slots=(slot,),
        )

        # Make another lesson with the same slot which we'll try adding the teacher to
        lesson = data_factories.Lesson(
            school=school,
            year_group=yg,
            user_defined_time_slots=(slot,),
        )
        assert lesson.teacher != teacher

        # Navigate to the first lesson_'s detail view
        url = UrlName.LESSON_UPDATE.url(lesson_id=lesson.lesson_id)
        form_partial = self.hx_get(url)

        # Check response ok
        assert form_partial.status_code == 200

        form = form_partial.forms["update-form"]

        # Fill in and post the form
        form["teacher"] = teacher.id

        response = form.submit(name="update-submit")

        # Check response ok
        assert response.status_code == 200

        # Check for relevant error message and lesson_ not updated
        django_form = response.context["form"]
        error_message = django_form.errors.as_text()
        assert "Cannot update teacher" in error_message

        lesson.refresh_from_db()
        assert lesson.teacher != teacher
