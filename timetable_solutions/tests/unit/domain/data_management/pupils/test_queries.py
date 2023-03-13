"""
Tests for data management pupil queries.
"""

# Third party imports
import pytest

# Local application imports
from domain.data_management.pupils import queries
from tests import data_factories


@pytest.mark.django_db
class TestGetPupils:
    @pytest.mark.parametrize("search_name", ["John", "john"])
    @pytest.mark.parametrize("name_type", ["firstname", "surname"])
    def test_gets_pupil_matching_name(self, search_name: str, name_type: str):
        pupil = data_factories.Pupil(**{name_type: "John"})
        data_factories.Pupil(school=pupil.school, firstname="Dave", surname="Dave")

        pupils = queries.get_pupils(
            school_id=pupil.school.school_access_key, search_term=search_name
        )

        assert pupils.get() == pupil

    def test_gets_pupil_matching_year_group(self):
        pupil = data_factories.Pupil(firstname="John", surname="John")
        data_factories.Pupil(school=pupil.school, firstname="John", surname="John")

        pupils = queries.get_pupils(
            school_id=pupil.school.school_access_key, year_group=pupil.year_group
        )

        assert pupils.get() == pupil

    def test_gets_pupil_matching_pupil_id(self):
        pupil = data_factories.Pupil()
        data_factories.Pupil(
            school=pupil.school,
        )

        pupils = queries.get_pupils(
            school_id=pupil.school.school_access_key, search_term=str(pupil.pupil_id)
        )

        assert pupils.get() == pupil


@pytest.mark.django_db
class TestGetNextIdForSchool:
    def test_gets_next_pupil_id_when_school_has_pupils(self):
        school = data_factories.School()
        pupil_a = data_factories.Pupil(school=school)
        pupil_b = data_factories.Pupil(school=school)

        next_id = queries.get_next_pupil_id_for_school(
            school_id=school.school_access_key
        )

        assert next_id == max(pupil_a.pupil_id, pupil_b.pupil_id) + 1

    def test_gets_one_when_school_has_no_pupils(self):
        school = data_factories.School()

        next_id = queries.get_next_pupil_id_for_school(
            school_id=school.school_access_key
        )

        assert next_id == 1
