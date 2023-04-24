"""
Tests for data management lesson queries.
"""

# Third party imports
import pytest

# Local application imports
from domain.data_management.lesson import queries
from tests import data_factories


@pytest.mark.django_db
class TestGetLessons:
    def test_gets_lesson_matching_lesson_id(self):
        target = data_factories.Lesson()

        # Make a lesson matching the lesson_id but not the school
        other_lesson = data_factories.Lesson(lesson_id=target.lesson_id)
        assert other_lesson.school != target.school

        # Make a lesson matching the school not the lesson_id
        another_lesson = data_factories.Lesson(school=target.school)
        assert another_lesson.lesson_id != target.lesson_id

        filtered_lessons = queries.get_lessons(
            school_id=target.school_id, search_term=target.lesson_id
        )

        assert filtered_lessons.get() == target

    def test_gets_lesson_matching_subject_name(self):
        target = data_factories.Lesson()

        # Make a lesson matching the subject name but not the school
        other_lesson = data_factories.Lesson(subject_name=target.subject_name)
        assert other_lesson.school != target.school

        # Make a lesson matching the school not the subject name
        another_lesson = data_factories.Lesson(subject_name="Something different")
        assert another_lesson.subject_name != target.subject_name

        filtered_lessons = queries.get_lessons(
            school_id=target.school_id, search_term=target.subject_name
        )

        assert filtered_lessons.get() == target
