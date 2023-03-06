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

    def test_serialize_teacher_queryset(self):
        teacher_a = data_factories.Teacher(firstname="AAA")
        teacher_b = data_factories.Teacher(firstname="BBB")
        queryset = models.Teacher.objects.all().order_by("firstname")

        serialized_teacher = serializers.Teacher(queryset, many=True).data

        assert serialized_teacher == [
            serializers_helpers.expected_teacher(teacher_a),
            serializers_helpers.expected_teacher(teacher_b),
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

    def test_serialize_teacher_queryset(self):
        yg_a = data_factories.YearGroup(year_group_name="AAA")
        yg_b = data_factories.YearGroup(year_group_name="BBB")
        queryset = models.YearGroup.objects.all().order_by("year_group_name")

        serialized_year_groups = serializers.YearGroup(queryset, many=True).data

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

    def test_serialize_lesson_queryset(self):
        lesson_a = data_factories.Lesson.with_n_pupils(lesson_id="AAA")
        lesson_b = data_factories.Lesson.with_n_pupils(lesson_id="BBB")
        lessons = models.Lesson.objects.all().order_by("lesson_id")

        serialized_lesson = serializers.Lesson(lessons, many=True).data

        assert serialized_lesson == [
            serializers_helpers.expected_lesson(lesson_a),
            serializers_helpers.expected_lesson(lesson_b),
        ]
