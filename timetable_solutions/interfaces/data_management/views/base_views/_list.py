# Standard library imports
from typing import Any, ClassVar, Generic, TypeVar

# Third party imports
from rest_framework import serializers

# Django imports
from django.contrib.auth import mixins
from django.db import models as django_models
from django.views import generic

# Local application imports
from interfaces.constants import UrlName
from interfaces.utils.typing_utils import AuthenticatedHttpRequest

_ModelT = TypeVar("_ModelT", bound=django_models.Model)


class ListView(mixins.LoginRequiredMixin, generic.ListView, Generic[_ModelT]):
    """
    Page displaying a school's data for a single model.

    Searches should be sent as GET requests from <input name='search-submit' ...> tags.
    """

    # Defaulted django vars
    paginate_by: ClassVar[int] = 50
    """Render 50 items per page, including for search results."""

    http_method_names = ["get"]
    """This is a read only page."""

    # Other class vars
    model_class: type[_ModelT]
    """The model who's data is rendered on this page."""

    serializer_class: type[serializers.Serializer[_ModelT]]
    """Serializer used to convert the queryset context into JSON-like data."""

    prefetch_related: list[django_models.Prefetch] | None = None
    """Any relationships to prefetch when retrieving the queryset."""

    displayed_fields: ClassVar[dict[str, str]]
    """
    The fields to use as column headers in the rendered context.
    Given as {field name: displayed name, ...} key-value pairs.
    The first key should always be the model's id within the school field, e.g. 'teacher_id'.
    """

    update_url: ClassVar[UrlName]
    """
    URL to go through to the detail view of individual objects.
    Needs reversing with an id kwarg in the template.
    """

    # Instance vars
    school_id: int
    """The school who's data will be shown."""

    def setup(
        self, request: AuthenticatedHttpRequest, *args: object, **kwargs: object
    ) -> None:
        """Set some instance attributes used in later logic."""
        super().setup(request, *args, **kwargs)
        self.school_id = request.user.profile.school.school_access_key

    def get_queryset(self) -> list[dict]:
        """Retrieve all the school's data for this model."""
        queryset = self.model_class.objects.get_all_instances_for_school(
            school_id=self.school_id
        )
        if self.prefetch_related:
            queryset = queryset.prefetch_related(*self.prefetch_related)
        return self.serialize_queryset(queryset)

    def serialize_queryset(
        self, queryset: django_models.QuerySet[_ModelT]
    ) -> list[dict]:
        """Serialize the queryset into a more primitive JSON-like data structure."""
        return self.serializer_class(queryset, many=True).data

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """
        Include a queryset in the context.

        This is either the return of the user's search, or all model data for their school.
        """
        context = super().get_context_data(**kwargs)
        context["update_url"] = self.update_url
        context["displayed_fields"] = self.displayed_fields
        context["model_name_singular"] = self.model_class.Constant.human_string_singular
        context["model_name_plural"] = self.model_class.Constant.human_string_plural
        return context
