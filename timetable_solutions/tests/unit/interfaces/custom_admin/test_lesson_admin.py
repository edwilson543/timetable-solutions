"""
Unit tests for the LessonModelAdmin class.
"""

# Django imports
from django import test
from django.contrib.auth.models import User

# Local application imports
from data import models
from interfaces.custom_admin import admin


class TestLessonModelAdmin(test.TestCase):

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "lessons_with_solution.json",
                "test_scenario_1.json"]  # Included since some data not corresponding to access key 123456 is needed

    lesson_url = "/data/admin/data/lesson/"

    # SAVE MODEL TESTS
    def test_save_model_from_valid_change_form(self):
        """
        Test for posting a valid CHANGE form to the admin (for an existing model) Lesson.
        This should automatically associate the user with the school.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = self.lesson_url + "1/change/"
        lesson_id = "YEAR_ONE_MATHS_A"  # Note that this lesson already exists in the DB is vital
        form_data = {
            "lesson_id": lesson_id,
            "subject_name": "Maths", "total_required_slots": 10, "total_required_double_periods": 2,
            "teacher": 1, "classroom": 1, "pupils": [1, 2], "user_defined_time_slots": [1, 2]
         }

        # Execute test unit
        response = self.client.post(url, data=form_data)

        # Check outcome
        self.assertRedirects(response=response, expected_url=self.lesson_url)

        lesson = models.Lesson.objects.get_individual_lesson(school_id=123456, lesson_id=lesson_id)
        self.assertEqual(lesson.school, models.School.objects.get_individual_school(school_id=123456))

        expected_pupils = models.Pupil.objects.get_all_instances_for_school(
            school_id=123456).filter(pupil_id__in=[1, 2])
        self.assertQuerysetEqual(lesson.pupils.all(), expected_pupils, ordered=False)

        expected_slots = models.TimetableSlot.objects.get_specific_timeslots(school_id=123456, slot_ids=[1, 2])
        self.assertQuerysetEqual(lesson.user_defined_time_slots.all(), expected_slots, ordered=False)

        # Check there is no solution present
        all_lessons = models.Lesson.objects.get_all_instances_for_school(school_id=123456)
        all_solver_slots = sum(lesson.solver_defined_time_slots.all().count() for lesson in all_lessons)
        assert all_solver_slots == 0

    def test_save_model_from_valid_add_form(self):
        """
        Test for posting a valid ADD form to the admin Lesson.
        This should automatically associate the user with the school.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = self.lesson_url + "add/"
        lesson_id = "TEST"  # Note that this lesson_id is unused
        form_data = {
            "lesson_id": lesson_id,
            "subject_name": "Maths", "total_required_slots": 10, "total_required_double_periods": 2,
            "teacher": 1, "classroom": 1, "pupils": [1, 2], "user_defined_time_slots": [1, 2]
        }

        # Execute test unit
        response = self.client.post(url, data=form_data)

        # Check outcome
        self.assertRedirects(response=response, expected_url=self.lesson_url)

        lesson = models.Lesson.objects.get_individual_lesson(school_id=123456, lesson_id=lesson_id)
        self.assertEqual(lesson.school, models.School.objects.get_individual_school(school_id=123456))

        expected_pupils = models.Pupil.objects.get_all_instances_for_school(
            school_id=123456).filter(pupil_id__in=[1, 2])
        self.assertQuerysetEqual(lesson.pupils.all(), expected_pupils, ordered=False)

        expected_slots = models.TimetableSlot.objects.get_specific_timeslots(school_id=123456, slot_ids=[1, 2])
        self.assertQuerysetEqual(lesson.user_defined_time_slots.all(), expected_slots, ordered=False)

        # Check there is no solution present
        all_lessons = models.Lesson.objects.get_all_instances_for_school(school_id=123456)
        all_solver_slots = sum(lesson.solver_defined_time_slots.all().count() for lesson in all_lessons)
        assert all_solver_slots == 0

    # GET QUERYSET TESTS
    def test_get_queryset_lessons_filters_by_school(self):
        """
        Test that the queryset of lessons for a user of school 123456 is restricted to their school only.
        """
        # Set test parameters
        factory = test.RequestFactory()
        request = factory.get(self.lesson_url)
        request.user = User.objects.get(username="dummy_teacher")
        lesson_admin = admin.LessonAdmin(model=models.Lesson, admin_site=admin.user_admin)

        # Execute test unit
        queryset = lesson_admin.get_queryset(request=request)

        # Check outcome
        expected_queryset = models.Lesson.objects.get_all_instances_for_school(school_id=123456)
        self.assertQuerysetEqual(queryset, expected_queryset, ordered=False)
