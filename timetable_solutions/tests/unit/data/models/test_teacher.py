"""
Unit tests for methods on the Teacher class
"""

# Third party imports
import pytest

# Django imports
from django import test
from django.db import IntegrityError
from django.db.models import ProtectedError

# Local application imports
from data import models


class TestTeacher(test.TestCase):

    fixtures = [
        "user_school_profile.json",
        "teachers.json",
        "classrooms.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
        "lessons_with_solution.json",
    ]

    # FACTORY METHOD TESTS
    def test_create_new_valid_teacher(self):
        """
        Tests that we can create and save a Teacher via the create_new method
        """
        # Execute test unit
        teacher = models.Teacher.create_new(
            school_id=123456,
            teacher_id=12,  # Note that id 12 is available
            firstname="test",
            surname="test",
            title="mr",
        )

        # Check outcome
        all_teachers = models.Teacher.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert teacher in all_teachers

    def test_create_new_fails_when_teacher_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two Teachers with the same id / school, due to unique_together on the Meta class
        """
        # Execute test unit
        with pytest.raises(IntegrityError):
            models.Teacher.create_new(
                school_id=123456,
                teacher_id=1,  # Note that id 1 is unavailable
                firstname="test",
                surname="test",
                title="mr",
            )

    def test_delete_all_instances_for_school_unsuccessful_when_attached_to_lessons(
        self,
    ):
        """
        Test that we cannot delete all teachers associated with a school, when there is at least one Lesson
        referencing the teachers we are trying to delete.
        """
        # Execute test unit
        with pytest.raises(ProtectedError):
            models.Teacher.delete_all_instances_for_school(school_id=123456)

    # FILTER METHOD TESTS
    def test_check_if_busy_at_timeslot_when_teacher_is_busy(self):
        """Test that the check_if_busy_at_time_slot method returns 'True' when we expect it to"""
        # Set test parameters
        teacher = models.Teacher.objects.get_individual_teacher(
            school_id=123456, teacher_id=1
        )
        slot = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=123456, slot_id=1
        )

        # Ensure they are busy at this time
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )
        lesson.teacher = teacher
        lesson.add_user_defined_time_slots(time_slots=slot)

        # Execute test unit
        is_busy = teacher.check_if_busy_at_timeslot(slot=slot)

        # Check outcome
        assert is_busy

    def test_check_if_busy_at_timeslot_when_teacher_is_not_busy(self):
        """Test that the check_if_busy_at_time_slot method returns 'False' when we expect it to"""
        # Set test parameters
        teacher = models.Teacher.objects.get_individual_teacher(
            school_id=123456, teacher_id=1
        )
        slot = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=123456, slot_id=5
        )

        # Execute test unit
        is_busy = teacher.check_if_busy_at_timeslot(slot=slot)

        # Check outcome
        assert not is_busy

    # QUERY METHOD TESTS
    def test_get_lessons_per_week(self):
        """
        Test that the correct number of lessons per week is retrieved for a teacher.
        """
        # Set test parameters
        teacher = models.Teacher.objects.get_individual_teacher(
            school_id=123456, teacher_id=1
        )

        # Execute test unit
        n_lessons = teacher.get_lessons_per_week()

        # Check outcome
        assert n_lessons == 22  # Since it includes lunch


class TestTeacherLessFixtures(test.TestCase):
    """
    Test class only loading in the school / teacher fixtures, to avoid foreign key issues.
    """

    fixtures = ["user_school_profile.json", "teachers.json"]

    def test_delete_all_instances_for_school_successful(self):
        """
        Test that we can successfully delete all teachers associated with a school, when there are no Lessons
        instances referencing the teachers as foreign keys.
        """
        # Execute test unit
        outcome = models.Teacher.delete_all_instances_for_school(school_id=123456)

        # Check outcome
        deleted_ref = outcome[1]
        assert deleted_ref["data.Teacher"] == 11

        all_teachers = models.Teacher.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert all_teachers.count() == 0
