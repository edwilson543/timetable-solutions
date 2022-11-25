"""
Unit tests for the FixedClassQuerySet (custom manager of the FixedClass model), as well as FixedClass itself.
"""

# Third party imports
import pytest

# Django imports
from django import test
from django.db import IntegrityError

# Local application imports
from data import models


class TestLesson(test.TestCase):
    """
    Unit tests for the FixedClass model
    """
    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "lessons_with_solution.json"]

    # FACTORY METHOD TESTS
    def test_create_new_valid_fixed_class(self):
        """
        Tests that we can create and save a Lesson via the create_new method
        """
        # Set test parameters
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=123456)

        # Execute test unit
        lesson = models.Lesson.create_new(
            school_id=123456, lesson_id="TEST-A", subject_name="TEST", teacher_id=1, classroom_id=1, pupils=all_pupils,
            user_defined_time_slots=all_slots[1:3], solver_defined_time_slots=all_slots[11:13],
            total_required_slots=4, total_required_double_periods=2)

        # Check outcome
        all_lessons = models.Lesson.objects.get_all_instances_for_school(school_id=123456)
        assert lesson in all_lessons
        self.assertQuerysetEqual(all_pupils, lesson.pupils.all(), ordered=False)
        self.assertQuerysetEqual(all_slots[1:3], lesson.user_defined_time_slots.all(), ordered=False)
        self.assertQuerysetEqual(all_slots[11:13], lesson.solver_defined_time_slots.all(), ordered=False)

    def test_create_new_fails_when_pupil_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two Lessons with the same (lesson_id, school) combination,
        due to unique_together on the Meta class
        """
        # Execute test unit
        with pytest.raises(IntegrityError):
            models.Lesson.create_new(
                school_id=123456, lesson_id="YEAR_ONE_MATHS_A",  # This combo is already in the fixture
                subject_name="TEST", teacher_id=1, classroom_id=1,
                total_required_slots=4, total_required_double_periods=2)

    def test_delete_all_instances_for_school_successful(self):
        """
        Test that we can delete all the lessons associated with a school
        """
        # Initial check
        all_lessons = models.Lesson.objects.get_all_instances_for_school(school_id=123456)
        assert all_lessons.count() == 24

        # Execute test unit
        models.Lesson.delete_all_lessons_for_school(school_id=123456)

        # Check outcome
        assert all_lessons.count() == 0

    def test_delete_solver_solution_for_school_successful(self):
        """
        Test that we can delete the solver produced solution for a school
        """
        # Initial check
        all_lessons = models.Lesson.objects.get_all_instances_for_school(school_id=123456)
        all_solver_slots = sum(lesson.solver_defined_time_slots.all().count() for lesson in all_lessons)
        assert all_solver_slots == 100

        # Execute test unit
        models.Lesson.delete_solver_solution_for_school(school_id=123456)

        # Check outcome
        all_solver_slots = sum(lesson.solver_defined_time_slots.all().count() for lesson in all_lessons)
        assert all_solver_slots == 0

        # Check no slots deleted
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=123456)
        assert all_slots.count() == 35
