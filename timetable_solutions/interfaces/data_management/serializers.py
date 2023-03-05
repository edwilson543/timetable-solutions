"""Serializer classes for the basic school data models."""

# Standard library imports
from collections import OrderedDict

# Third party imports
from rest_framework import serializers

# Local application imports
from data import models
from interfaces.constants import UrlName


class Teacher(serializers.Serializer):
    """Serialize teacher instance for use in template context."""

    teacher_id = serializers.IntegerField()
    firstname = serializers.CharField()
    surname = serializers.CharField()
    title = serializers.CharField()
    update_url = serializers.SerializerMethodField(method_name="_get_update_url")

    def _get_update_url(self, obj: models.Teacher) -> str:
        """Get the url leading to this teacher's update / detail view page."""
        return UrlName.TEACHER_UPDATE.url(teacher_id=obj.teacher_id)


class YearGroup(serializers.Serializer):
    """Serialize a lesson instance for use in template context."""

    year_group_id = serializers.IntegerField()
    year_group_name = serializers.CharField()


class Lesson(serializers.Serializer):
    """Serialize a lesson instance for use in template context."""

    lesson_id = serializers.CharField()
    subject_name = serializers.CharField()
    year_group = serializers.SerializerMethodField(method_name="_year_group")
    teacher = serializers.SerializerMethodField(method_name="_teacher")
    total_required_slots = serializers.IntegerField()

    def _year_group(self, obj: models.Lesson) -> str:
        return obj.get_associated_year_group().year_group_name

    def _teacher(self, obj: models.Lesson) -> OrderedDict:
        return Teacher(obj.teacher).data
