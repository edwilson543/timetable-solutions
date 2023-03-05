"""Serializer classes for the basic school data models."""

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
