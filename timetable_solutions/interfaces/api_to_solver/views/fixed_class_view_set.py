# Third party imports
from rest_framework import response
from rest_framework import status

# Local application imports
from .model_view_set_base_class import CustomModelViewSet
from interfaces.api_to_solver import serialisers


class FixedClass(CustomModelViewSet):
    """
    ViewSet for the FixedClass model, which allows for:
        GET requests to a specific school's data;
        POST requests of individual or list of FixedClass model instances
    """
    serializer_class = serialisers.FixedClass
    http_method_names = ["get", "post"]

    def create(self, request, *args, **kwargs):
        """
        Customisation of the default create method to offer the flexibility for FixedClass instances to either be
        POSTed to the API individually, or as a list of instances.
        """
        if isinstance(request.data, dict):
            # In this case a single FixedClass instance is being posted (represented by a dict)
            return super().create(request, *args, **kwargs)
        elif isinstance(request.data, list):
            # In this case multiple FixedClass instances are being posted (represented by a list of dicts)
            serializer = self.get_serializer(data=request.data, many=True)  # Note the many=True kwarg
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
