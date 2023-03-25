"""Unit tests for Break model operations"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import constants, models
from domain.data_management.break_ import operations
from tests import data_factories


@pytest.mark.django_db
class TestCreateNewBreak:
    def test_create_new_for_valid_break(self):
        # Get some teachers and year groups to add
        school = data_factories.School()
        data_factories.Teacher(school=school)
        data_factories.YearGroup(school=school)

        # Make the break
        break_ = operations.create_new_break(
            school_id=school.school_access_key,
            break_id="1",
            break_name="Morning break",
            starts_at=dt.time(hour=11, minute=30),
            ends_at=dt.time(hour=12),
            day_of_week=constants.Day.MONDAY,
            teachers=models.Teacher.objects.all(),
            relevant_year_groups=models.YearGroup.objects.all(),
        )

        # Check break in db and defined as expected
        assert break_ == models.Break.objects.get()

        assert break_.school == school
        assert break_.break_id == "1"
        assert break_.break_name
        assert break_.teachers.get() == models.Teacher.objects.get()
        assert break_.relevant_year_groups.get() == models.YearGroup.objects.get()

    def test_raises_when_break_id_already_taken(self):
        break_ = data_factories.Break()

        # Try to make another break with the same id
        with pytest.raises(operations.UnableToCreateBreak) as exc:
            operations.create_new_break(
                school_id=break_.school.school_access_key,
                break_id=break_.break_id,
                break_name="Morning break",
                starts_at=dt.time(hour=11, minute=30),
                ends_at=dt.time(hour=12),
                day_of_week=constants.Day.MONDAY,
                teachers=models.Teacher.objects.all(),
                relevant_year_groups=models.YearGroup.objects.all(),
            )

        assert (
            "Could not create break with the given data."
            in exc.value.human_error_message
        )

    def test_creates_new_break_relevant_to_all_year_groups(self):
        # Get some teachers and year groups to add
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)

        # Make the break
        break_ = operations.create_new_break(
            school_id=school.school_access_key,
            break_id="1",
            break_name="Morning break",
            starts_at=dt.time(hour=11, minute=30),
            ends_at=dt.time(hour=12),
            day_of_week=constants.Day.MONDAY,
            teachers=models.Teacher.objects.none(),
            relevant_to_all_year_groups=True,
        )

        # Check break in db and defined as expected
        assert break_ == models.Break.objects.get()
        assert break_.relevant_year_groups.get() == yg

    def test_creates_new_break_relevant_to_all_teachers(self):
        # Get some teachers and year groups to add
        school = data_factories.School()
        teachers = data_factories.Teacher(school=school)

        # Make the break
        break_ = operations.create_new_break(
            school_id=school.school_access_key,
            break_id="1",
            break_name="Morning break",
            starts_at=dt.time(hour=11, minute=30),
            ends_at=dt.time(hour=12),
            day_of_week=constants.Day.MONDAY,
            relevant_year_groups=models.YearGroup.objects.none(),
            relevant_to_all_teachers=True,
        )

        # Check break in db and defined as expected
        assert break_ == models.Break.objects.get()
        assert break_.teachers.get() == teachers


@pytest.mark.django_db
class TestUpdateBreakTimings:
    def test_can_update_break_to_valid_time(self):
        break_ = data_factories.Break()

        updated_break = operations.update_break_timings(
            break_=break_,
            day_of_week=constants.Day.FRIDAY,
            starts_at=dt.time(hour=15),
            ends_at=dt.time(hour=16),
        )

        assert updated_break.day_of_week == constants.Day.FRIDAY
        assert updated_break.starts_at == dt.time(hour=15)
        assert updated_break.ends_at == dt.time(hour=16)

    def test_raises_if_updating_break_to_invalid_time(self):
        break_ = data_factories.Break()

        with pytest.raises(operations.UnableToUpdateBreakTimings):
            operations.update_break_timings(
                break_=break_,
                day_of_week=constants.Day.FRIDAY,
                starts_at=dt.time(hour=16),
                ends_at=dt.time(hour=15),
            )


@pytest.mark.django_db
class TestUpdateBreakYearGroups:
    def test_can_update_relevant_year_groups(self):
        break_ = data_factories.Break()

        yg_a = data_factories.YearGroup(school=break_.school)
        yg_b = data_factories.YearGroup(school=break_.school)
        ygs = models.YearGroup.objects.all()

        updated_break = operations.update_break_year_groups(
            break_=break_, relevant_year_groups=ygs
        )

        assert updated_break.relevant_year_groups.count() == 2
        assert yg_a in updated_break.relevant_year_groups.all()
        assert yg_b in updated_break.relevant_year_groups.all()


@pytest.mark.django_db
class TestDeleteBreak:
    def test_can_delete_timetable_break(self):
        break_ = data_factories.Break()

        operations.delete_break(break_)

        with pytest.raises(models.Break.DoesNotExist):
            break_.refresh_from_db()
