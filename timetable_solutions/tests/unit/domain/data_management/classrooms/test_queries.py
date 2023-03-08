"""
Tests for data management classroom queries.
"""

# Third party imports
import pytest

# Local application imports
from domain.data_management.classrooms import queries
from tests import data_factories


@pytest.mark.django_db
class TestGetNextIdForSchool:
    def test_gets_next_classroom_id_when_school_has_classrooms(self):
        school = data_factories.School()
        classroom_a = data_factories.Classroom(school=school)
        classroom_b = data_factories.Classroom(school=school)

        next_id = queries.get_next_classroom_id_for_school(
            school_id=school.school_access_key
        )

        assert next_id == max(classroom_a.classroom_id, classroom_b.classroom_id) + 1

    def test_gets_one_when_school_has_no_classrooms(self):
        school = data_factories.School()

        next_id = queries.get_next_classroom_id_for_school(
            school_id=school.school_access_key
        )

        assert next_id == 1
