"""
Tests for data management classroom queries.
"""

# Third party imports
import pytest

# Local application imports
from domain.data_management.classrooms import queries
from tests import data_factories


@pytest.mark.django_db
class TestGetClassrooms:
    def test_gets_classroom_matching_id(self):
        classroom = data_factories.Classroom(classroom_id=1)
        data_factories.Classroom(classroom_id=2)

        classrooms = queries.get_classrooms(
            school_id=classroom.school.school_access_key,
            classroom_id=classroom.classroom_id,
        )

        assert classrooms.get() == classroom

    def test_gets_classroom_matching_building(self):
        classroom = data_factories.Classroom(building="Maths")
        data_factories.Classroom(building="Science")

        classrooms = queries.get_classrooms(
            school_id=classroom.school.school_access_key,
            building=classroom.building,
        )

        assert classrooms.get() == classroom

    def test_gets_classroom_matching_room_number(self):
        classroom = data_factories.Classroom(room_number=10)
        data_factories.Classroom(room_number=11)

        classrooms = queries.get_classrooms(
            school_id=classroom.school.school_access_key,
            room_number=classroom.room_number,
        )

        assert classrooms.get() == classroom

    def test_gets_classroom_matching_multiple_params(self):
        classroom = data_factories.Classroom(building="Maths", room_number=10)
        data_factories.Classroom(room_number=10)
        data_factories.Classroom(building="Science")

        classrooms = queries.get_classrooms(
            school_id=classroom.school.school_access_key,
            building=classroom.building,
            room_number=classroom.room_number,
        )

        assert classrooms.get() == classroom


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
