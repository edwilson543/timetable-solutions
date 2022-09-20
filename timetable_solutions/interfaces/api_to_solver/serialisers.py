"""
Django-rest framework serializer classes for the models that are required by the solver.
The solver only needs to be aware of FixedClass, UnsolvedClass, and TimetableSlot - all other models e.g. pupils are
identifiable from the model field relationships, and suffice to be represented by primary keys only within the solver.
"""

# Third party imports
from rest_framework import serializers

# Local application imports
from data import models


class FixedClass(serializers.ModelSerializer):
    """Serialiser for the FixedClass model, implementing all model fields"""
    class Meta:
        model = models.FixedClass
        fields = ["school", "class_id", "subject_name", "teacher", "classroom", "pupils", "time_slots", "user_defined"]


class UnsolvedClass(serializers.ModelSerializer):
    """
    Serialiser for the UnsolvedClass model, implementing all model fields except 'school' which is not needed since
    unsolved classes will only ever be transferred to the solver and not Posted by the solver.
    """
    class Meta:
        model = models.UnsolvedClass
        fields = ["class_id", "subject_name", "teacher", "pupils", "classroom", "total_slots", "min_distinct_slots"]


class TimetableSlot(serializers.ModelSerializer):
    """Serialiser for the TimetableSlot model, implementing all model fields except 'school' which is not needed since
    unsolved classes will only ever be transferred to the solver and not Posted by the solver."""
    class Meta:
        model = models.TimetableSlot
        fields = ["slot_id", "day_of_week", "period_starts_at", "period_duration"]
