"""Unit tests for pupil operations"""

# Third party imports
import pytest

# Local application imports
from data import models
from domain.data_management.pupils import exceptions, operations
from tests import data_factories


@pytest.mark.django_db
class TestCreateNewPupil:
    def test_create_new_valid_pupil(self):
        # Make a school and year group for the pupil to be associated with
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)

        # Create a new pupil for the school
        operations.create_new_pupil(
            school_id=school.school_access_key,
            year_group_id=yg.year_group_id,
            pupil_id=100,
            firstname="test",
            surname="test",
        )

        # Check pupil was created
        pupil = models.Pupil.objects.get()

        assert pupil.school == school
        assert pupil.year_group == yg
        assert pupil.pupil_id == 100
        assert pupil.pk == 1

    def test_raises_when_pupil_id_not_unique_for_school(self):
        pupil = data_factories.Pupil()

        with pytest.raises(exceptions.CouldNotCreatePupil):
            operations.create_new_pupil(
                school_id=pupil.school.school_access_key,
                year_group_id=pupil.year_group.year_group_id,
                pupil_id=pupil.pupil_id,
                firstname="test",
                surname="test",
            )

    def test_raises_when_year_group_does_not_exist(self):
        school = data_factories.School()

        with pytest.raises(exceptions.CouldNotCreatePupil):
            operations.create_new_pupil(
                school_id=school.school_access_key,
                year_group_id=100,  # Does not exist
                pupil_id=10,
                firstname="test",
                surname="test",
            )
