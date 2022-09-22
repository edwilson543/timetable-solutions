# Third party imports
from rest_framework import status
from rest_framework import viewsets


class CustomModelViewSet(viewsets.ModelViewSet):
    """
    Tailoring of the implementation of the DRF ModelViewSet for the purposes of this application.
    In particular, we want to be able to GET the data relevant to one specific school.
    """

    def get_queryset(self, *args, **kwargs):
        """
        Tailoring of 'get_queryset' to allow access to a specific school's UnsolvedClass instances.
        Data for one school can then be accessed by querying the full list of pupils with a school access key, e.g.:
        /api/<model_url>/?school_access_key=123456
        """
        school_access_key = self.request.query_params.get("school_access_key")
        if school_access_key is not None:
            try:
                school_access_key = int(school_access_key)
                queryset = self.serializer_class.Meta.model.objects.get_all_instances_for_school(
                    school_id=school_access_key)
                return queryset
            except ValueError:
                return None

    def list(self, request, *args, **kwargs):
        """
        Custom implementation of the list method to allow provision of status code 204 when no data is available
        corresponding to the queried school_access_key.
        """
        response = super().list(request, *args, **kwargs)
        if len(response.data) == 0:
            response.status_code = status.HTTP_204_NO_CONTENT
        return response
