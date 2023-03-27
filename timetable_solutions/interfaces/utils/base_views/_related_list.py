# Standard library imports
from typing import Any, ClassVar, Generic, TypeVar

# Third party imports
from rest_framework import serializers

# Django imports
from django import http
from django.contrib.auth import mixins
from django.db import models as django_models
from django.views import generic

# Local application imports
from interfaces.constants import UrlName
from interfaces.utils.base_views import _htmx_views
from interfaces.utils.typing_utils import AuthenticatedHttpRequest

ModelT = TypeVar("ModelT", bound=django_models.Model)
RelatedModelT = TypeVar("RelatedModelT", bound=django_models.Model)


class RelatedListPartialView(
    _htmx_views.HTMXViewMixin,
    mixins.LoginRequiredMixin,
    generic.ListView,
    Generic[ModelT, RelatedModelT],
):
    """
    View providing some related objects for a single model instance.

    Note this view will only ever render a template partial.
    """

    model_class: type[ModelT]
    """The model who's data is rendered on this page."""

    related_name: ClassVar[str]
    """Name of the related manager on the model class."""

    related_model_name: ClassVar[str]
    """Title of the related model to show in the html template."""

    object_id_name: ClassVar[str]
    """Name of this model's id field, that is unique to the school (not the related model's). """

    page_url_prefix: ClassVar[UrlName]
    """
    Prefix of this partial's url.
    The full url is constructed as page_url_prefix/<model_instance_id>/<related_name>.
    """

    serializer_class: type[serializers.Serializer[ModelT]]
    """Serializer used to convert the RELATED queryset context into JSON-like data."""

    displayed_fields: ClassVar[dict[str, str]]
    """
    The fields of the RELATED object to use as column headers in the rendered context.
    Given as {field name: displayed name, ...} key-value pairs.
    The first key should always be the model's id within the school field, e.g. 'teacher_id'.
    Note the field names need to match those of the serializer class.
    """

    # Defaulted django vars
    paginate_by: ClassVar[int] = 10
    """Render 50 items per page, including for search results."""

    template_name = "utils/tables/related-objects-table.html"
    """Default partial that will be rendered."""

    # Instance vars
    model_instance: ModelT
    """The model whose related objects we are viewing."""

    model_instance_id: int | str
    """A kwarg in any url routed to a subclass of this view."""

    object_list: django_models.QuerySet[RelatedModelT]
    """The items that will be displayed in the related objects table."""

    school_id: int
    """The school who's data will be shown."""

    def setup(
        self, request: AuthenticatedHttpRequest, *args: object, **kwargs: Any
    ) -> None:
        super().setup(request, *args, **kwargs)
        self.school_id = request.user.profile.school.school_access_key
        self.model_instance_id = kwargs[self.object_id_name]
        self.model_instance = self.get_model_instance()

    def dispatch(
        self, request: http.HttpRequest, *args: object, **kwargs: object
    ) -> http.HttpResponseBase:
        """
        Disallow requests that did not come from htmx.
        """
        if not self.is_htmx:
            raise http.Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """
        Add the url used to update the table.
        """
        context = super().get_context_data(**kwargs)
        context["related_name"] = self.related_name
        context["related_table_url"] = self.related_table_url
        context["displayed_fields"] = self.displayed_fields
        context["related_model_name"] = self.related_model_name
        return context

    def get_queryset(self) -> list[dict]:
        """
        Retrieve and serialize the related objects of the target model instance.
        """
        queryset = getattr(self.model_instance, self.related_name).all()
        return self.serializer_class(instance=queryset, many=True).data

    def get_model_instance(self) -> ModelT:
        """
        Get the object we are viewing the related objects of.
        """
        objects = self.model_class.objects.prefetch_related(self.related_name)
        try:
            return objects.get(
                school_id=self.school_id,
                **{self.object_id_name: self.model_instance_id}
            )
        except self.model_class.DoesNotExist:
            raise http.Http404

    @property
    def related_table_url(self) -> str:
        """Construct the full page url."""
        return self.page_url_prefix.url(
            lazy=False, **{self.object_id_name: self.model_instance_id}
        )
