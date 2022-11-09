"""
Tests for the views that handle the resetting of user data.
"""

# Django imports
from django import test
from django import urls

# Local application imports
from constants.url_names import UrlName
from data import models


class TestDataResetViews(test.TestCase):
    """
    Tests for the post method supplied by each subclass of DataResetBase
    """

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json", "fixed_classes_lunch.json"]

    def test_pupil_reset_resets_pupils_and_fixed_unsolved_classes(self):
        """
        Test that attempting to reset the pupil data for a school will do this, and as well as reset the FixedClass
        and UnsolvedClass models for the school.
        """
        # Set test parameters
        url = urls.reverse(UrlName.PUPIL_LIST_RESET.value)
        self.client.login(username="dummy_teacher", password="dt123dt123")
        expected_redirect_url = urls.reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.post(url)

        # Check outcome
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        all_unsolved_classes = models.UnsolvedClass.objects.get_all_instances_for_school(school_id=123456)
        relevant_fixed_classes = models.FixedClass.objects.get_user_defined_fixed_classes(school_id=123456)
        assert all_pupils.count() == all_unsolved_classes.count() == relevant_fixed_classes.count() == 0

        self.assertRedirects(response, expected_url=expected_redirect_url)

    def test_teacher_reset_resets_teachers_and_fixed_unsolved_classes(self):
        """
        Test that attempting to reset the teacher data for a school will do this, and as well as reset the FixedClass
        and UnsolvedClass models for the school.
        """
        # Set test parameters
        url = urls.reverse(UrlName.TEACHER_LIST_RESET.value)
        self.client.login(username="dummy_teacher", password="dt123dt123")
        expected_redirect_url = urls.reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.post(url)

        # Check outcome
        all_teachers = models.Teacher.objects.get_all_instances_for_school(school_id=123456)
        all_unsolved_classes = models.UnsolvedClass.objects.get_all_instances_for_school(school_id=123456)
        relevant_fixed_classes = models.FixedClass.objects.get_user_defined_fixed_classes(school_id=123456)
        assert all_teachers.count() == all_unsolved_classes.count() == relevant_fixed_classes.count() == 0

        self.assertRedirects(response, expected_url=expected_redirect_url)

    def test_classroom_reset_resets_classrooms_and_fixed_unsolved_classes(self):
        """
        Test that attempting to reset the classroom data for a school will do this, and as well as reset the FixedClass
        and UnsolvedClass models for the school.
        """
        # Set test parameters
        url = urls.reverse(UrlName.CLASSROOM_LIST_RESET.value)
        self.client.login(username="dummy_teacher", password="dt123dt123")
        expected_redirect_url = urls.reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.post(url)

        # Check outcome
        all_classrooms = models.Classroom.objects.get_all_instances_for_school(school_id=123456)
        all_unsolved_classes = models.UnsolvedClass.objects.get_all_instances_for_school(school_id=123456)
        relevant_fixed_classes = models.FixedClass.objects.get_user_defined_fixed_classes(school_id=123456)
        assert all_classrooms.count() == all_unsolved_classes.count() == relevant_fixed_classes.count() == 0

        self.assertRedirects(response, expected_url=expected_redirect_url)

    def test_timetable_reset_resets_timetable_slots_and_fixed_unsolved_classes(self):
        """
        Test that attempting to reset the timetable data for a school will do this, and as well as reset the FixedClass
        and UnsolvedClass models for the school.
        """
        # Set test parameters
        url = urls.reverse(UrlName.TIMETABLE_STRUCTURE_RESET.value)
        self.client.login(username="dummy_teacher", password="dt123dt123")
        expected_redirect_url = urls.reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.post(url)

        # Check outcome
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=123456)
        all_unsolved_classes = models.UnsolvedClass.objects.get_all_instances_for_school(school_id=123456)
        relevant_fixed_classes = models.FixedClass.objects.get_user_defined_fixed_classes(school_id=123456)
        assert all_slots.count() == all_unsolved_classes.count() == relevant_fixed_classes.count() == 0

        self.assertRedirects(response, expected_url=expected_redirect_url)

    def test_fixed_class_reset_resets_just_fixed_classes(self):
        """
        Test that attempting to reset the FixedClass data for a school is successful
        """
        # Set test parameters
        url = urls.reverse(UrlName.FIXED_CLASSES_RESET.value)
        self.client.login(username="dummy_teacher", password="dt123dt123")
        expected_redirect_url = urls.reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.post(url)

        # Check outcome
        relevant_fixed_classes = models.FixedClass.objects.get_user_defined_fixed_classes(school_id=123456)
        assert relevant_fixed_classes.count() == 0

        self.assertRedirects(response, expected_url=expected_redirect_url)

    def test_unsolved_class_reset_resets_just_unsolved_classes(self):
        """
        Test that attempting to reset the timetable data for a school is successful.
        """
        # Set test parameters
        url = urls.reverse(UrlName.UNSOLVED_CLASSES_RESET.value)
        self.client.login(username="dummy_teacher", password="dt123dt123")
        expected_redirect_url = urls.reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.post(url)

        # Check outcome
        all_unsolved_classes = models.UnsolvedClass.objects.get_all_instances_for_school(school_id=123456)
        assert all_unsolved_classes.count() == 0

        self.assertRedirects(response, expected_url=expected_redirect_url)
