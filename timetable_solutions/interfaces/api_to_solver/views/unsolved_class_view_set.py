# Local application imports
from interfaces.api_to_solver import serialisers
from .model_view_set_base_class import CustomModelViewSet


class UnsolvedClass(CustomModelViewSet):
    """
    ViewSet for the UnsolvedClass.
    The solver needs to be able to GET UnsolvedClass data to understand what it is trying to solve.
    """
    serializer_class = serialisers.UnsolvedClass
    http_method_names = ["get"]
