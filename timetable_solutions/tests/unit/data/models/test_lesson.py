"""
Unit tests for the Lesson model and its manager, LessonQuerySet.
"""

# Third party imports
import pytest

# Django imports
from django import test
from django.core import management
from django.db import IntegrityError

# Local application imports
from data import models


class TestLesson(test.TestCase):
    """
    Unit tests for the Lesson model
    """

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
    def test_create_new_valid_lesson(self):
        """
        Tests that we can create and save a Lesson via the create_new method
        """
        # Set test parameters
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=123456
        )

        # Execute test unit
        lesson = models.Lesson.create_new(
            school_id=123456,
            lesson_id="TEST-A",
            subject_name="TEST",
            teacher_id=1,
            classroom_id=1,
            pupils=all_pupils,
            user_defined_time_slots=all_slots[1:3],
            solver_defined_time_slots=all_slots[11:13],
            total_required_slots=4,
            total_required_double_periods=2,
        )

        # Check outcome
        all_lessons = models.Lesson.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert lesson in all_lessons
        self.assertQuerysetEqual(all_pupils, lesson.pupils.all(), ordered=False)
        self.assertQuerysetEqual(
            all_slots[1:3], lesson.user_defined_time_slots.all(), ordered=False
        )
        self.assertQuerysetEqual(
            all_slots[11:13], lesson.solver_defined_time_slots.all(), ordered=False
        )

    def test_create_new_fails_when_pupil_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two Lessons with the same (lesson_id, school) combination,
        due to unique_together on the Meta class
        """
        # Execute test unit
        with pytest.raises(IntegrityError):
            models.Lesson.create_new(
                school_id=123456,
                lesson_id="YEAR_ONE_MATHS_A",  # This combo is already in the fixture
                subject_name="TEST",
                teacher_id=1,
                classroom_id=1,
                total_required_slots=4,
                total_required_double_periods=2,
            )

    def test_delete_all_instances_for_school_successful(self):
        """
        Test that we can delete all the lessons associated with a school
        """
        # Initial check
        all_lessons = models.Lesson.objects.get_all_instances_for_school(
            school_id=123456
        )
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
        all_lessons = models.Lesson.objects.get_all_instances_for_school(
            school_id=123456
        )
        all_solver_slots = sum(
            lesson.solver_defined_time_slots.all().count() for lesson in all_lessons
        )
        assert all_solver_slots == 100

        # Execute test unit
        models.Lesson.delete_solver_solution_for_school(school_id=123456)

        # Check outcome
        all_solver_slots = sum(
            lesson.solver_defined_time_slots.all().count() for lesson in all_lessons
        )
        assert all_solver_slots == 0

        # Check no slots deleted
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert all_slots.count() == 35

    # QUERY METHOD TESTS
    def test_get_all_timeslots_for_lesson_with_user_and_solver(self):
        """
        Test that the get all timeslots method correctly combines the solver / user time slot querysets
        """
        # Set test parameters
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )
        additional_slots = models.TimetableSlot.objects.filter(slot_id__in=[3, 4, 5])
        lesson.user_defined_time_slots.add(*additional_slots)

        # Execute test unit
        all_slots = lesson.get_all_time_slots()

        # Check outcome
        expected_total = (
            lesson.user_defined_time_slots.all().count()
            + lesson.solver_defined_time_slots.all().count()
        )
        assert all_slots.count() == expected_total

    def test_get_lessons_requiring_solving(self):
        """
        Method to check that the correct subset of lessons is extracted for the solver.
        """
        # Execute test unit
        solver_lessons = models.Lesson.get_lessons_requiring_solving(school_id=123456)

        # Check outcome
        assert solver_lessons.count() == 12
        for subject_name in {lesson.subject_name for lesson in solver_lessons}:
            assert "LUNCH" not in subject_name  # We know when lunch is

    def test_get_n_solver_slots_required(self):
        """
        Method to check that the correct number of solver slots is calculated for a lesson
        """
        # Set test parameters
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )
        additional_slots = models.TimetableSlot.objects.filter(slot_id__in=[3, 4, 5])
        lesson.user_defined_time_slots.add(*additional_slots)

        # Execute test unit
        n_slots = lesson.get_n_solver_slots_required()

        # Check outcome
        assert n_slots == 5  # = 8 - 3, since we added 3 in the setup

    def test_get_n_solver_double_periods_required(self):
        """
        Method to check that the correct number of solver double periods is calculated for a lesson
        """
        # Set test parameters
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )
        additional_slots = models.TimetableSlot.objects.filter(
            slot_id__in=[1, 6]
        )  # Add a double, to reduce count
        lesson.user_defined_time_slots.add(*additional_slots)

        # Execute test unit
        n_doubles = lesson.get_n_solver_double_periods_required()

        # Check outcome
        assert n_doubles == 2

    def test_requires_solving_true(self):
        """
        Method to check that a lesson with unfulfilled slots requires solving
        """
        # Set test parameters
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )
        additional_slots = models.TimetableSlot.objects.filter(slot_id__in=[3, 4, 5])
        lesson.user_defined_time_slots.add(*additional_slots)

        # Execute test unit
        requires_solving = lesson.requires_solving()

        # Check outcome
        assert requires_solving

    def test_requires_solving_false(self):
        """
        Method to check that a lesson with unfulfilled slots requires solving
        """
        # Set test parameters
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="LUNCH_PUPILS"
        )

        # Execute test unit
        requires_solving = lesson.requires_solving()

        # Check outcome
        assert not requires_solving

    def test_get_user_defined_double_period_count_on_day_one_double_expected(self):
        """
        Unit test that the method for counting the number of double periods defined by the user for a Lesson
        with ONE double period is correct.
        """
        # Set test parameters
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )
        lesson.user_defined_time_slots.add(
            *lesson.solver_defined_time_slots.all()
        )  # Manually give some user slots
        monday = models.WeekDay.MONDAY.value

        # Execute test unit
        double_period_count = lesson.get_user_defined_double_period_count_on_day(
            day_of_week=monday
        )

        # Check outcome
        assert double_period_count == 1

    def test_get_user_defined_double_period_count_on_day_no_doubles_expected(self):
        """
        Unit test that the method for counting the number of double periods defined by the user for a Lesson
        with ZERO double periods is correct.
        """
        # Set test parameters
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )
        lesson.user_defined_time_slots.add(
            *lesson.solver_defined_time_slots.all()
        )  # Manually give some user slots
        tuesday = models.WeekDay.TUESDAY.value

        # Execute test unit
        double_period_count = lesson.get_user_defined_double_period_count_on_day(
            day_of_week=tuesday
        )

        # Check outcome
        assert double_period_count == 0

    def test_get_year_group_str_for_lesson_with_pupils(self):
        """
        Test that the correct year group for a lesson (with pupils and therefore a year group) is returned.
        """
        # Set test parameters
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )

        # Execute test unit
        year_group = lesson.get_year_group_str()

        # Check outcome
        assert year_group == "1"

    def test_get_year_group_str_for_lesson_without_pupils(self):
        """
        Test that N/A is returned as the year group when a lesson has no pupils.
        """
        # Set test parameters
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="LUNCH_1"
        )

        # Execute test unit
        year_group = lesson.get_year_group_str()

        # Check outcome
        assert year_group == "N/A"

    def test_get_associated_timeslots_year_one_lesson(self):
        """
        Test that the corrct set of timeslots for year one is retrieved.
        """
        # Set test parameters
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )

        # Execute test unit
        slots = lesson.get_associated_timeslots()

        # Check outcome
        assert slots.count() == 35

    def test_get_associated_timeslots_extra_year_lesson(self):
        """
        Test that the corrct set of timeslots for the 'extra year' is retrieved.
        """
        # Set test parameters
        management.call_command("loaddata", "extra-year.json")
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="extra-year-history"
        )

        # Execute test unit
        slots = lesson.get_associated_timeslots()

        # Check outcome
        assert slots.count() == 2
