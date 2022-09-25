"""Django-rest framework model serializer class for the FixedClass model."""

# Third party imports
from rest_framework import serializers

# Local application imports
from data import models


class FixedClass(serializers.ModelSerializer):
    """Serialiser for the FixedClass model, implementing all model fields"""
    class Meta:
        model = models.FixedClass
        fields = ["school", "class_id", "subject_name", "teacher", "classroom", "pupils", "time_slots", "user_defined"]

