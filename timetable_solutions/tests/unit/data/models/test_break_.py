# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Django imports
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Local application imports
from data import constants, models
from tests import data_factories


@pytest.mark.django_db
class TestBreakQuerySet:
    def test_get_all_instances_for_school(self):
        break_ = data_factories.Break()

        # Make a break at another school
        data_factories.Break()

        breaks = models.Break.objects.get_all_instances_for_school(
            school_id=break_.school.school_access_key
        )

        assert breaks.get() == break_

    def test_get_all_instances_for_school_with_breaks(self):
        yg = data_factories.YearGroup()
        break_ = data_factories.Break(relevant_year_groups=(yg,), school=yg.school)

        # Make a break with no year groups
        data_factories.Break(school=yg.school)

        # Make a break at another school
        data_factories.Break()

        breaks = models.Break.objects.get_all_instances_for_school_with_year_groups(
            school_id=break_.school.school_access_key
        )

        assert breaks.get() == break_


@pytest.mark.django_db
class TestCreateNewBreak:
    def test_create_new_for_valid_break(self):
        # Get some teachers and year groups to add
        school = data_factories.School()
        teacher = data_factories.Teacher()
        yg = data_factories.YearGroup()

        # Make the break
        break_ = models.Break.create_new(
            school_id=school.school_access_key,
            break_id="1",
            break_name="Morning break",
            starts_at=dt.time(hour=11, minute=30),
            ends_at=dt.time(hour=12),
            day_of_week=constants.Day.MONDAY,
            teachers=teacher,
            relevant_year_groups=yg,
        )

        # Check break in db and defined as expected
        all_breaks = models.Break.objects.all()
        assert all_breaks.count() == 1
        assert break_ in all_breaks

        all_teachers = break_.teachers.all()
        assert all_teachers.count() == 1
        assert teacher in all_teachers

        all_ygs = break_.relevant_year_groups.all()
        assert all_ygs.count() == 1
        assert yg in all_ygs

    def test_create_new_raises_when_break_id_already_taken(self):
        break_ = data_factories.Break()

        # Try to make another break with the same id
        with pytest.raises(IntegrityError):
            models.Break.create_new(
                school_id=break_.school.school_access_key,
                break_id=break_.break_id,
                break_name="test",
                starts_at=dt.time(hour=11, minute=30),
                ends_at=dt.time(hour=12),
                day_of_week=constants.Day.MONDAY,
                teachers=models.Teacher.objects.none(),
                relevant_year_groups=models.YearGroup.objects.none(),
            )

    def test_create_new_raises_when_break_ends_before_it_starts(self):
        school = data_factories.School()

        # Try to make another break with the same id
        with pytest.raises(IntegrityError):
            models.Break.create_new(
                school_id=school.school_access_key,
                break_id="morning-break",
                break_name="test",
                starts_at=dt.time(hour=12),
                ends_at=dt.time(hour=11),  # Note ends after starts
                day_of_week=constants.Day.MONDAY,
                teachers=models.Teacher.objects.none(),
                relevant_year_groups=models.YearGroup.objects.none(),
            )

    def test_create_new_raises_when_break_ends_when_it_starts(self):
        school = data_factories.School()

        # Try to make another break with the same id
        with pytest.raises(IntegrityError):
            models.Break.create_new(
                school_id=school.school_access_key,
                break_id="morning-break",
                break_name="test",
                starts_at=dt.time(hour=12),
                ends_at=dt.time(hour=12),  # Note ends at same time
                day_of_week=constants.Day.MONDAY,
                teachers=models.Teacher.objects.none(),
                relevant_year_groups=models.YearGroup.objects.none(),
            )

    def test_create_new_raises_for_invalid_day_of_week(self):
        school = data_factories.School()

        # Try to make another break with the same id
        with pytest.raises(ValidationError):
            models.Break.create_new(
                school_id=school.school_access_key,
                break_id="morning-break",
                break_name="test",
                starts_at=dt.time(hour=12),
                ends_at=dt.time(hour=13),
                day_of_week=100,
                teachers=models.Teacher.objects.none(),
                relevant_year_groups=models.YearGroup.objects.none(),
            )


@pytest.mark.django_db
class TestDeleteAllInstancesForSchool:
    def test_delete_all_breaks_for_school_successful(self):
        """
        Test that we can delete all the breaks associated with a school.
        """
        # Make a break
        break_ = data_factories.Break()

        # Try deleting the break
        models.Break.delete_all_breaks_for_school(
            school_id=break_.school.school_access_key
        )

        # Check break was deleted
        assert models.Break.objects.count() == 0
