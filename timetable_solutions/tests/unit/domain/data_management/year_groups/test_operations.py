"""Unit tests for year group operations"""

# Third party imports
import pytest

# Local application imports
from data import models
from domain.data_management.year_groups import operations
from tests import data_factories


@pytest.mark.django_db
class TestCreateNewYearGroup:
    @pytest.mark.parametrize("year_group_id", [1, None])
    def test_creates_year_group_in_db_for_valid_params(self, year_group_id: int | None):
        # Make a school for the year group
        school = data_factories.School()

        # Try creating year group
        operations.create_new_year_group(
            school_id=school.school_access_key,
            year_group_id=year_group_id,
            year_group_name="test",
        )

        # Check year group was created
        all_ygs = models.YearGroup.objects.all()
        yg = all_ygs.get()

        assert yg.year_group_id == 1
        assert yg.year_group_name == "test"

    def test_raises_when_year_group_id_not_unique_for_school(self):
        # Make a year group to occupy an id value
        yg = data_factories.YearGroup()
        school = yg.school

        # Try making a year group with the same school / id
        with pytest.raises(operations.UnableToCreateYearGroup) as exc:
            operations.create_new_year_group(
                school_id=school.school_access_key,
                year_group_id=yg.year_group_id,
                year_group_name="test",
            )

        assert f"Year group with this data already exists!" in str(
            exc.value.human_error_message
        )

    def test_raises_when_year_group_name_not_unique_for_school(self):
        # Make a year group to occupy an id value
        yg = data_factories.YearGroup()
        school = yg.school

        # Try making a year group with the same school / id
        with pytest.raises(operations.UnableToCreateYearGroup) as exc:
            operations.create_new_year_group(
                school_id=school.school_access_key,
                year_group_id=yg.year_group_id + 1,
                year_group_name=yg.year_group_name,
            )

        assert f"Year group with this data already exists!" in str(
            exc.value.human_error_message
        )


@pytest.mark.django_db
class TestUpdateYearGroup:
    def test_updates_year_group_name(self):
        yg = data_factories.YearGroup(year_group_name="not-test")

        operations.update_year_group(year_group=yg, year_group_name="test")

        yg.refresh_from_db()

        assert yg.year_group_name == "test"


@pytest.mark.django_db
class TestDeleteYearGroup:
    def test_delete_year_group_with_no_pupils(self):
        yg = data_factories.YearGroup()

        operations.delete_year_group(yg)

        with pytest.raises(models.YearGroup.DoesNotExist):
            yg.refresh_from_db()

    def test_deleting_year_group_also_deletes_pupils(self):
        pupil = data_factories.Pupil()
        yg = pupil.year_group

        operations.delete_year_group(yg)

        with pytest.raises(models.YearGroup.DoesNotExist):
            yg.refresh_from_db()

        with pytest.raises(models.Pupil.DoesNotExist):
            pupil.refresh_from_db()

    def test_deleting_year_group_removes_relation_with_timetable_slots(self):
        yg = data_factories.YearGroup()
        slot = data_factories.TimetableSlot(
            school=yg.school, relevant_year_groups=(yg,)
        )

        operations.delete_year_group(yg)

        with pytest.raises(models.YearGroup.DoesNotExist):
            yg.refresh_from_db()

        slot.refresh_from_db()
        assert slot.relevant_year_groups.count() == 0

    def test_deleting_year_group_removes_relation_with_break(self):
        yg = data_factories.YearGroup()
        break_ = data_factories.Break(school=yg.school, relevant_year_groups=(yg,))

        operations.delete_year_group(yg)

        with pytest.raises(models.YearGroup.DoesNotExist):
            yg.refresh_from_db()

        break_.refresh_from_db()
        assert break_.relevant_year_groups.count() == 0
