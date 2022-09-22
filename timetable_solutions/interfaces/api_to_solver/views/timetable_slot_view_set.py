# Third party imports
from rest_framework import viewsets

# Local application imports
from data import models
from interfaces.api_to_solver import serialisers


class TimetableSlot(viewsets.ModelViewSet):
    """
    ViewSet for the Timetable - which the solver needs to be able to GET to understand the parameters (i.e. the
    available slots) for when the classes can be allocated.
    """
    serializer_class = serialisers.TimetableSlot
    http_method_names = ["get"]

    def get_queryset(self, *args, **kwargs):
        """Customisation of the get_queryset method to allow access to a specific school's TimetableSlot instances"""
        school_access_key = self.request.query_params.get("school_access_key")
        if school_access_key is not None:
            try:
                school_access_key = int(school_access_key)
                slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=school_access_key)
                return slots
            except ValueError:
                # TODO in this instance ensure response status code is 204
                return None
        else:
            return None
