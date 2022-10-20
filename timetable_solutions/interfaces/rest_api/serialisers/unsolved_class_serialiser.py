"""Django-rest framework model serializer class for the UnsolvedClass model."""

# Third party imports
from rest_framework import serializers

# Local application imports
from data import models


class UnsolvedClass(serializers.ModelSerializer):
    """
    Serialiser for the UnsolvedClass model, implementing all model fields except 'school' which is not needed since
    unsolved classes will only ever be transferred to the solver and not Posted by the solver.
    """
    class Meta:
        model = models.UnsolvedClass
        fields = ["class_id", "subject_name", "teacher", "pupils", "classroom", "total_slots", "n_double_periods"]
