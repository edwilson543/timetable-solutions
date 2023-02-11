"""
Unit tests for the custom management command used to load in some dummy data (load_all_fixtures)
"""

# Django imports
from django import test
from django.core.management import call_command
from django.contrib.auth.models import User

# Local application imports
from data import models


class TestLoadAllFixturesCommand(test.TestCase):
    """
    Class defining the tests for the load_all_fixtures custom management command
    """

    def test_load_all_fixtures_do_not_include_solution(self):
        """
        Unit test for the parameterless call to load all fixtures - which specifically does not load in any non-user-
        defined time slots.
        """
        # Execute test unit
        call_command("load_all_fixtures")

        # Test outcome
        assert User.objects.all().count() == 1
        assert models.School.objects.all().count() == 1
        assert models.Profile.objects.all().count() == 1
        assert models.YearGroup.objects.all().count() == 3
        assert models.Classroom.objects.all().count() == 12
        assert models.Pupil.objects.all().count() == 6
        assert models.Teacher.objects.all().count() == 11
        assert models.TimetableSlot.objects.all().count() == 30
        assert models.Break.objects.all().count() == 5

        all_lessons = models.Lesson.objects.all()
        assert all_lessons.count() == 12

        total_solver_produced_slots = sum(
            lesson.solver_defined_time_slots.all().count() for lesson in all_lessons
        )
        assert total_solver_produced_slots == 0

    def test_load_all_fixtures_include_solution(self):
        """
        Unit test for the load_all_fixtures command when we do want to load in all of the fixed classes.
        """
        # Execute test unit
        call_command("load_all_fixtures", "--include_solution")

        # Test outcome
        assert User.objects.all().count() == 1
        assert models.School.objects.all().count() == 1
        assert models.Profile.objects.all().count() == 1
        assert models.YearGroup.objects.all().count() == 3
        assert models.Classroom.objects.all().count() == 12
        assert models.Pupil.objects.all().count() == 6
        assert models.Teacher.objects.all().count() == 11
        assert models.TimetableSlot.objects.all().count() == 30
        assert models.Break.objects.all().count() == 5

        all_lessons = models.Lesson.objects.all()
        assert all_lessons.count() == 12

        total_solver_produced_slots = sum(
            lesson.solver_defined_time_slots.all().count() for lesson in all_lessons
        )
        assert total_solver_produced_slots == 100

    def test_load_all_fixtures_when_all_data_is_already_present(self):
        """
        Unit test for the load_all_fixtures command when all the fixtures have already been loaded into the database.
        The aim is to check that the entries don't get duplicated.
        """
        # Execute test unit (twice)
        call_command("load_all_fixtures", "--include_solution")
        call_command("load_all_fixtures", "--include_solution")

        # Test outcome
        assert User.objects.all().count() == 1
        assert models.School.objects.all().count() == 1
        assert models.Profile.objects.all().count() == 1
        assert models.YearGroup.objects.all().count() == 3
        assert models.Classroom.objects.all().count() == 12
        assert models.Pupil.objects.all().count() == 6
        assert models.Teacher.objects.all().count() == 11
        assert models.TimetableSlot.objects.all().count() == 30
        assert models.Break.objects.all().count() == 5

        all_lessons = models.Lesson.objects.all()
        assert all_lessons.count() == 12

        total_solver_produced_slots = sum(
            lesson.solver_defined_time_slots.all().count() for lesson in all_lessons
        )
        assert total_solver_produced_slots == 100
