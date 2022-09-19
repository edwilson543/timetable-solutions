

# Third party imports
from rest_framework import viewsets

# Local application imports
from data import models
from interfaces.api_to_solver import serialisers


class FixedClassViewSet(viewsets.ModelViewSet):
    """Viewset for the FixedClass model"""
    serializer_class = serialisers.FixedClassSerialiser
    queryset = models.FixedClass.objects.all()  # TODO replace with method on the queryset manager
