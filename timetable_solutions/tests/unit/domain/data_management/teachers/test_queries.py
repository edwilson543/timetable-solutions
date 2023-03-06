"""Tests for data management teacher queries."""

# Third party imports
import pytest

# Local application imports
from domain.data_management.teachers import queries
from tests import data_factories


@pytest.mark.django_db
class TestGetTeacherBySearchTerm:
    """Tests for the get_teachers_by_search_term function."""

    # --------------------
    # Tests for searches by id
    # --------------------

    def test_includes_teacher_with_matching_id(self):
        searched_id = 1
        search_school = data_factories.School()
        teacher = data_factories.Teacher(school=search_school, teacher_id=searched_id)

        teachers = queries.get_teachers_by_search_term(
            school_id=search_school.school_access_key, search_term=str(searched_id)
        )

        assert teachers.count() == 1
        queried_teacher = teachers.first()
        assert queried_teacher == teacher

    def test_does_not_include_teacher_at_same_school_not_matching_id(self):
        searched_id = 1
        search_school = data_factories.School()

        # Include a teacher at search_school but with a non-matching id
        data_factories.Teacher(school=search_school, teacher_id=(searched_id * 10))

        teachers = queries.get_teachers_by_search_term(
            school_id=search_school.school_access_key, search_term=str(searched_id)
        )

        assert teachers.count() == 0

    def test_does_not_include_teacher_at_different_school_with_matching_id(self):
        searched_id = 1
        search_school = data_factories.School()

        # Include a teacher with a matching id but at some school
        other_school = data_factories.School()
        data_factories.Teacher(school=other_school, teacher_id=searched_id)

        teachers = queries.get_teachers_by_search_term(
            school_id=search_school.school_access_key, search_term=str(searched_id)
        )

        assert teachers.count() == 0

    # --------------------
    # Tests for searches by firstname / surname
    # --------------------

    @pytest.mark.parametrize("search_term", ["John", "john", "j"])
    @pytest.mark.parametrize("firstname", [True, False])
    def test_return_has_single_teacher_with_matching_name(
        self, search_term: str, firstname: bool
    ):
        # Make a teacher to be the target of the search
        if firstname:
            teacher = data_factories.Teacher(firstname="John")
        else:
            teacher = data_factories.Teacher(surname="John")

        teachers = queries.get_teachers_by_search_term(
            school_id=teacher.school.school_access_key, search_term=search_term
        )

        assert teachers.count() == 1
        queried_teacher = teachers.first()
        assert queried_teacher == teacher

    def test_returns_teacher_when_full_name_searched(self):
        # Make a teacher to be the target of the search
        teacher = data_factories.Teacher(firstname="John", surname="Doe")

        teachers = queries.get_teachers_by_search_term(
            school_id=teacher.school.school_access_key, search_term="John Doe"
        )

        assert teachers.count() == 1
        queried_teacher = teachers.first()
        assert queried_teacher == teacher

    def test_does_not_include_non_matching_name(self):
        # Make a teacher with some non-matching name
        teacher = data_factories.Teacher(firstname="Dave", surname="Dave")

        teachers = queries.get_teachers_by_search_term(
            school_id=teacher.school.school_access_key, search_term="John"
        )

        assert teachers.count() == 0

    @pytest.mark.parametrize("firstname", [True, False])
    def test_return_does_not_include_teacher_at_other_school(self, firstname: bool):
        search_school = data_factories.School()

        # Make a teacher at another school
        other_school = data_factories.School()
        teacher = data_factories.Teacher(school=other_school)

        if firstname:
            search_term = teacher.firstname
        else:
            search_term = teacher.surname
        teachers = queries.get_teachers_by_search_term(
            school_id=search_school.school_access_key, search_term=search_term
        )

        assert teachers.count() == 0

    @pytest.mark.parametrize("firstname", [True, False])
    @pytest.mark.parametrize("n_term_splits", [2, 6, 100])
    def test_matches_name_by_splitting_search_term(
        self, firstname: bool, n_term_splits: int
    ):
        # The search term will not immediately match the name, but once split in 2 it should.
        search_term = "johnny"

        if firstname:
            teacher = data_factories.Teacher(firstname="John")
        else:
            teacher = data_factories.Teacher(surname="John")

        teachers = queries.get_teachers_by_search_term(
            school_id=teacher.school.school_access_key,
            search_term=search_term,
            n_term_splits=n_term_splits,
        )

        assert teachers.count() == 1
        queried_teacher = teachers.first()
        assert queried_teacher == teacher


@pytest.mark.django_db
class TestGetTeacherForSchool:
    def test_gets_teacher(self):
        teacher = data_factories.Teacher()

        got_teacher = queries.get_teacher_for_school(
            school_id=teacher.school.school_access_key, teacher_id=teacher.teacher_id
        )

        assert got_teacher == teacher

    def test_gets_none_when_teacher_doesnt_exist(self):
        school = data_factories.School()

        teacher = queries.get_teacher_for_school(
            school_id=school.school_access_key, teacher_id=1
        )

        assert teacher is None


@pytest.mark.django_db
class TestGetNextIdForSchool:
    def test_gets_next_teacher_id_when_school_has_teachers(self):
        school = data_factories.School()
        teacher_a = data_factories.Teacher(school=school)
        teacher_b = data_factories.Teacher(school=school)

        next_id = queries.get_next_teacher_id_for_school(
            school_id=school.school_access_key
        )

        assert next_id == max(teacher_a.teacher_id, teacher_b.teacher_id) + 1

    def test_gets_one_when_school_has_no_teachers(self):
        school = data_factories.School()

        next_id = queries.get_next_teacher_id_for_school(
            school_id=school.school_access_key
        )

        assert next_id == 1
