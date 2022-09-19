# Third party imports
from rest_framework import viewsets

# Local application imports
from data import models
from interfaces.api_to_solver import serialisers


class FixedClassViewSet(viewsets.ModelViewSet):
    """Viewset for the FixedClass model"""
    serializer_class = serialisers.FixedClassSerialiser

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

# TODO UnsolvedClassViewSet; make fixture for unsolved classes (from csv)

# TODO TimetableSlotViewSet
