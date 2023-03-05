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

    def test_serialize_teacher_queryset(self):
        teacher_a = data_factories.Teacher(firstname="AAA")
        teacher_b = data_factories.Teacher(firstname="BBB")
        queryset = models.Teacher.objects.all().order_by("firstname")

        serialized_teacher = serializers.Teacher(queryset, many=True).data

        assert serialized_teacher == [
            serializers_helpers.expected_teacher(teacher_a),
            serializers_helpers.expected_teacher(teacher_b),
        ]
