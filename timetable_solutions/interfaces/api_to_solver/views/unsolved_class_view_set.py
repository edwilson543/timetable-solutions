# Third party imports
from rest_framework import status
from rest_framework import viewsets

# Local application imports
from data import models
from interfaces.api_to_solver import serialisers


# TODO create a custom subclass of the ModelViewSet implementing .get_queryset() and .list()
class UnsolvedClass(viewsets.ModelViewSet):
    """
    ViewSet for the UnsolvedClass - which the solver needs to be able to GET to understand what it is trying to
    solve.
    """
    serializer_class = serialisers.UnsolvedClass
    http_method_names = ["get"]

    def get_queryset(self, *args, **kwargs):
        """Customisation of the get_queryset method to allow access to a specific school's UnsolvedClass instances"""
        school_access_key = self.request.query_params.get("school_access_key")
        if school_access_key is not None:
            try:
                school_access_key = int(school_access_key)
                unsolved_classes = models.UnsolvedClass.objects.get_all_instances_for_school(
                    school_id=school_access_key)
                return unsolved_classes
            except ValueError:
                # TODO in this instance ensure response status code is 204
                return None
        else:
            return None

    def list(self, request, *args, **kwargs):
        """
        Custom implementation of the list method to allow provision of status code 204 when no data corresponds
        to the school access key.
        """
        response = super().list(request, *args, **kwargs)
        if len(response.data) == 0:
            response.status_code = status.HTTP_204_NO_CONTENT
        return response
