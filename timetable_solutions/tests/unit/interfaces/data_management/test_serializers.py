"""Tests for serializer classes for the basic school data models."""

# Third party imports
import pytest

# Local application imports
from data import models
from interfaces.data_management import serializers
from tests import data_factories
from tests.helpers import serializers as serializers_helpers


@pytest.mark.django_db
class TestTeacherSerializer:
    def test_serialize_individual_instance(self):
        teacher = data_factories.Teacher()

        serialized_teacher = serializers.Teacher(teacher).data

        assert serialized_teacher == serializers_helpers.expected_teacher(teacher)

    def test_serialize_individual_instance_with_lesson(self):
        lesson = data_factories.Lesson.with_n_pupils()
        teacher = lesson.teacher

        serialized_teacher = serializers.Teacher(teacher).data

        assert serialized_teacher == serializers_helpers.expected_teacher(teacher)

    def test_serialize_multiple_teachers(self):
        teacher_a = data_factories.Teacher()
        teacher_b = data_factories.Teacher()

        serialized_teacher = serializers.Teacher([teacher_a, teacher_b], many=True).data

        assert serialized_teacher == [
            serializers_helpers.expected_teacher(teacher_a),
            serializers_helpers.expected_teacher(teacher_b),
        ]


@pytest.mark.django_db
class TestClassroomSerializer:
    def test_serialize_individual_instance(self):
        classroom = data_factories.Classroom()

        serialized_classroom = serializers.Classroom(classroom).data

        assert serialized_classroom == serializers_helpers.expected_classroom(classroom)

    def test_serialize_individual_instance_with_lesson(self):
        lesson = data_factories.Lesson.with_n_pupils()
        classroom = lesson.classroom

        serialized_classroom = serializers.Classroom(classroom).data

        assert serialized_classroom == serializers_helpers.expected_classroom(classroom)

    def test_serialize_multiple_classrooms(self):
        classroom_a = data_factories.Classroom()
        classroom_b = data_factories.Classroom()

        serialized_classrooms = serializers.Classroom(
            [classroom_a, classroom_b], many=True
        ).data

        assert serialized_classrooms == [
            serializers_helpers.expected_classroom(classroom_a),
            serializers_helpers.expected_classroom(classroom_b),
        ]


@pytest.mark.django_db
class TestYearGroupSerializer:
    def test_serialize_individual_instance_no_pupils(self):
        year_group = data_factories.YearGroup()

        serialized_year_group = serializers.YearGroup(year_group).data

        assert serialized_year_group == serializers_helpers.expected_year_group(
            year_group
        )

    def test_serialize_individual_instance_with_pupils(self):
        pupil = data_factories.Pupil()
        year_group = pupil.year_group

        serialized_year_group = serializers.YearGroup(year_group).data

        assert serialized_year_group == serializers_helpers.expected_year_group(
            year_group
        )

    def test_serialize_multiple_year_groups(self):
        yg_a = data_factories.YearGroup()
        yg_b = data_factories.YearGroup()

        serialized_year_groups = serializers.YearGroup([yg_a, yg_b], many=True).data

        assert serialized_year_groups == [
            serializers_helpers.expected_year_group(yg_a),
            serializers_helpers.expected_year_group(yg_b),
        ]


@pytest.mark.django_db
class TestLessonSerializer:
    def test_serialize_individual_instance(self):
        lesson = data_factories.Lesson.with_n_pupils()

        serialized_lesson = serializers.Lesson(lesson).data

        assert serialized_lesson == serializers_helpers.expected_lesson(lesson)

    def test_serialize_multiple_lessons(self):
        lesson_a = data_factories.Lesson.with_n_pupils()
        lesson_b = data_factories.Lesson.with_n_pupils()

        serialized_lesson = serializers.Lesson([lesson_a, lesson_b], many=True).data

        assert serialized_lesson == [
            serializers_helpers.expected_lesson(lesson_a),
            serializers_helpers.expected_lesson(lesson_b),
        ]
