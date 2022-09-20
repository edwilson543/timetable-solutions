# Third party imports
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets

# Local application imports
from data import models
from interfaces.api_to_solver import serialisers


class FixedClass(viewsets.ModelViewSet):
    """
    Viewset for the FixedClass model, which allows for GET requests to a specific school's data, and POST request
    of individual or list of FixedClass model instances
    """
    serializer_class = serialisers.FixedClass

    def get_queryset(self):
        """
        Optionally restricts the returned serialised FixedClass instances, by checking the url for filtering against a
        specific school.
        e.g. domain/api/fixedclasses?school_access_key=123456
        """
        school_access_key = self.request.query_params.get("school_access_key")
        if school_access_key is not None:
            try:
                school_access_key = int(school_access_key)
                fixed_classes = models.FixedClass.objects.get_all_school_fixed_classes(school_id=school_access_key)
                return fixed_classes
            except ValueError:  # URL query specified a school access key but it was not an integer
                # TODO in this instance ensure response status code is 204
                return None
        else:
            return None

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

# TODO UnsolvedClassViewSet; make fixture for unsolved classes (from csv)

# TODO TimetableSlotViewSet
