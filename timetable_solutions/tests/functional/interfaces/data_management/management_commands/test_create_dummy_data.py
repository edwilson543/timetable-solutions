# Third party imports
import pytest

# Django imports
from django.contrib.auth.models import User
from django.core.management import base as base_command
from django.core.management import call_command

# Local application imports
from data import constants, models
from interfaces.data_management.management.commands import create_dummy_data
from tests import data_factories


@pytest.mark.django_db
class TestCreateDummyData:
    def test_creates_dummy_data_in_db_and_new_school(self):
        call_command("create_dummy_data", "--school-access-key=1")

        assert models.School.objects.count() == 1
        assert User.objects.count() == 101
        assert models.Profile.objects.count() == 101

        assert models.YearGroup.objects.count() == create_dummy_data.n_year_groups
        assert models.Pupil.objects.count() == (
            create_dummy_data.n_year_groups
            * create_dummy_data.pupils_per_class
            * create_dummy_data.classes_per_year_group
        )

        assert models.Classroom.objects.count() == models.Teacher.objects.count() == 9

        assert models.TimetableSlot.objects.count() == len(constants.Day.weekdays()) * 8
        assert models.Break.objects.count() == len(constants.Day.weekdays()) * len(
            ["Morning break", "Lunch"]
        )

        assert (
            models.Lesson.objects.count()
            == len(create_dummy_data.subject_lessons_per_week)
            * create_dummy_data.n_year_groups
            * create_dummy_data.classes_per_year_group
        )

    def test_raises_for_school_that_already_has_data(self):
        school = data_factories.School()

        with pytest.raises(base_command.CommandError):
            call_command(
                "create_dummy_data", f"--school-access-key={school.school_access_key}"
            )

    def test_raises_for_non_integer_school_access_key(self):
        with pytest.raises(base_command.CommandError):
            call_command("create_dummy_data", "--school-access-key=access-key")

    def test_raises_if_no_school_access_key_given(self):
        with pytest.raises(base_command.CommandError):
            call_command("create_dummy_data")
