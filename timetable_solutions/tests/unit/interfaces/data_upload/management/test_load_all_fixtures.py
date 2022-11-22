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
    def test_load_all_fixtures_do_not_include_fixed_classes(self):
        """
        Unit test for the parameterless call to load all fixtures - which specifically does not load in any non-user-
        defined FixedClass instances.
        """
        # Execute test unit
        call_command("load_all_fixtures")

        # Test outcome
        assert User.objects.all().count() == 1
        assert models.School.objects.all().count() == 1
        assert models.Profile.objects.all().count() == 1
        assert models.Classroom.objects.all().count() == 12
        assert models.Pupil.objects.all().count() == 6
        assert models.Teacher.objects.all().count() == 11
        assert models.TimetableSlot.objects.all().count() == 35
        assert models.UnsolvedClass.objects.all().count() == 12
        assert models.FixedClass.objects.all().count() == 12  # Note only 12 (12 lunch classes)

    def test_load_all_fixtures_include_fixed_classes(self):
        """
        Unit test for the load_all_fixtures command when we do want to load in all of the fixed classes.
        """
        # Execute test unit
        call_command("load_all_fixtures", "--include_fixed_classes")

        # Test outcome
        assert User.objects.all().count() == 1
        assert models.School.objects.all().count() == 1
        assert models.Profile.objects.all().count() == 1
        assert models.Classroom.objects.all().count() == 12
        assert models.Pupil.objects.all().count() == 6
        assert models.Teacher.objects.all().count() == 11
        assert models.TimetableSlot.objects.all().count() == 35
        assert models.UnsolvedClass.objects.all().count() == 12
        assert models.FixedClass.objects.all().count() == 24  # Note 24 (user defined and on user defined)

    def test_load_all_fixtures_when_all_data_is_already_present(self):
        """
        Unit test for the load_all_fixtures command when all the fixtures have already been loaded into the database.
        The aim is to check that the entries don't get duplicated.
        """
        # Execute test unit (twice)
        call_command("load_all_fixtures", "--include_fixed_classes")
        call_command("load_all_fixtures", "--include_fixed_classes")

        # Test outcome
        assert User.objects.all().count() == 1
        assert models.School.objects.all().count() == 1
        assert models.Profile.objects.all().count() == 1
        assert models.Classroom.objects.all().count() == 12
        assert models.Pupil.objects.all().count() == 6
        assert models.Teacher.objects.all().count() == 11
        assert models.TimetableSlot.objects.all().count() == 35
        assert models.UnsolvedClass.objects.all().count() == 12
        assert models.FixedClass.objects.all().count() == 24  # Note 24 (user defined and on user defined)
