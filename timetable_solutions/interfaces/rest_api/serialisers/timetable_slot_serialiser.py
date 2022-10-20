"""Django-rest framework model serializer class for the TimetableSlot model."""

# Third party imports
from rest_framework import serializers

# Local application imports
from data import models


class TimetableSlot(serializers.ModelSerializer):
    """Serialiser for the TimetableSlot model, implementing all model fields except 'school' which is not needed since
    unsolved classes will only ever be transferred to the solver and not Posted by the solver."""
    class Meta:
        model = models.TimetableSlot
        fields = ["slot_id", "day_of_week", "period_starts_at", "period_duration"]
