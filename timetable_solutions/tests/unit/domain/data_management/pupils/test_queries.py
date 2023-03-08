"""
Tests for data management pupil queries.
"""

# Third party imports
import pytest

# Local application imports
from domain.data_management.pupils import queries
from tests import data_factories


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
