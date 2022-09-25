# Local application imports
from .model_view_set_base_class import CustomModelViewSet
from interfaces.api_to_solver import serialisers


class TimetableSlot(CustomModelViewSet):
    """
    ViewSet for the Timetable.
    The solver must be able to GET the TimetableSlot instances, to understand the available slots to which the classes
    can be allocated.
    """
    serializer_class = serialisers.TimetableSlot
    http_method_names = ["get"]
