"""
Tests for the views that handle the resetting of user data.
"""

# Django imports
from django import test
from django import urls

# Local application imports
from interfaces.constants import UrlName
from data import models


class TestDataResetViews(test.TestCase):
    """
    Tests for the post method supplied by each subclass of DataResetBase
    """

    fixtures = [
        "user_school_profile.json",
        "classrooms.json",
        "teachers.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
        "lessons_with_solution.json",
    ]

    def test_teacher_reset_resets_teachers_and_lessons(self):
        """
        Test that attempting to reset the teacher data for a school will do this, and also reset the school's data in
        the Lesson model
        """
        # Set test parameters
        url = urls.reverse(UrlName.TEACHER_LIST_RESET.value)
        self.client.login(username="dummy_teacher", password="dt123dt123")
        expected_redirect_url = urls.reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.post(url)

        # Check outcome
        all_teachers = models.Teacher.objects.get_all_instances_for_school(
            school_id=123456
        )
        all_lessons = models.Lesson.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert all_teachers.count() == all_lessons.count() == 0

        self.assertRedirects(response, expected_url=expected_redirect_url)

    def test_classroom_reset_resets_classrooms_and_lessons(self):
        """
        Test that attempting to reset the classroom data for a school will do this, and also reset the school's data in
        the Lesson model
        """
        # Set test parameters
        url = urls.reverse(UrlName.CLASSROOM_LIST_RESET.value)
        self.client.login(username="dummy_teacher", password="dt123dt123")
        expected_redirect_url = urls.reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.post(url)

        # Check outcome
        all_classrooms = models.Classroom.objects.get_all_instances_for_school(
            school_id=123456
        )
        all_lessons = models.Lesson.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert all_classrooms.count() == all_lessons.count() == 0

        self.assertRedirects(response, expected_url=expected_redirect_url)

    def test_pupil_reset_resets_pupils_and_lessons(self):
        """
        Test that attempting to reset the pupil data for a school will do this, and also reset the school's data in
        the Lesson model
        """
        # Set test parameters
        url = urls.reverse(UrlName.PUPIL_LIST_RESET.value)
        self.client.login(username="dummy_teacher", password="dt123dt123")
        expected_redirect_url = urls.reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.post(url)

        # Check outcome
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        all_lessons = models.Lesson.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert all_pupils.count() == all_lessons.count() == 0

        self.assertRedirects(response, expected_url=expected_redirect_url)

    def test_timetable_reset_resets_timetable_slots_and_lessons(self):
        """
        Test that attempting to reset the timetable data for a school will do this, and also reset the school's data in
        the Lesson model
        """
        # Set test parameters
        url = urls.reverse(UrlName.TIMETABLE_STRUCTURE_RESET.value)
        self.client.login(username="dummy_teacher", password="dt123dt123")
        expected_redirect_url = urls.reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.post(url)

        # Check outcome
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=123456
        )
        all_lessons = models.Lesson.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert all_slots.count() == all_lessons.count() == 0

        self.assertRedirects(response, expected_url=expected_redirect_url)

    def test_year_group_reset_resets_year_groups_pupils_and_timetable_slots(self):
        """
        Test that attempting to reset the YearGroup data for a school resets that, along with
        the Pupil and TimetableSlot data (since these depend on the YearGroup model).
        """
        # Set test parameters
        url = urls.reverse(UrlName.YEAR_GROUP_RESET.value)
        self.client.login(username="dummy_teacher", password="dt123dt123")
        expected_redirect_url = urls.reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.post(url)

        # Check outcome
        all_ygs = models.YearGroup.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert all_ygs.count() == 0

        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert all_slots.count() == 0

        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        assert all_ygs.count() == all_pupils.count() == all_slots.count() == 0

        self.assertRedirects(response, expected_url=expected_redirect_url)

    def test_lesson_reset_resets_just_lessons(self):
        """
        Test that attempting to reset the Lesson data for a school is successful
        """
        # Set test parameters
        url = urls.reverse(UrlName.LESSONS_RESET.value)
        self.client.login(username="dummy_teacher", password="dt123dt123")
        expected_redirect_url = urls.reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.post(url)

        # Check outcome
        all_lessons = models.Lesson.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert all_lessons.count() == 0

        self.assertRedirects(response, expected_url=expected_redirect_url)

    def test_reset_all_view_resets_all_relevant_tables(self):
        """
        Test that a POST request to the reset all view will reset every table for a school
        """
        # Set test parameters
        url = urls.reverse(UrlName.ALL_DATA_RESET.value)
        self.client.login(username="dummy_teacher", password="dt123dt123")
        expected_redirect_url = urls.reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.post(url)

        # Check outcome
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        all_teachers = models.Teacher.objects.get_all_instances_for_school(
            school_id=123456
        )
        all_classrooms = models.Classroom.objects.get_all_instances_for_school(
            school_id=123456
        )
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=123456
        )
        all_lessons = models.Lesson.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert all_pupils.count() == all_teachers.count() == all_classrooms.count() == 0
        assert all_slots.count() == all_lessons.count() == 0

        self.assertRedirects(response, expected_url=expected_redirect_url)
