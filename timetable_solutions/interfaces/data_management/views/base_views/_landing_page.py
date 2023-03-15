# Standard library imports
import abc
from typing import Any, ClassVar

# Django imports
from django import http
from django.contrib.auth import mixins
from django.views import generic

# Local application imports
from data import models
from interfaces.constants import UrlName
from interfaces.utils.typing_utils import AuthenticatedHttpRequest


class LandingView(mixins.LoginRequiredMixin, generic.TemplateView):
    """Page users arrive at from the navbar, to manage the data of a single model."""

    # Default django vars
    template_name = "data_management/landing-page.html"
    http_method_names = ["get"]

    # Class vars
    model_class: ClassVar[type[models.ModelSubclass]]
    """The model that the landing page will allow users to manage the data of."""

    upload_url: ClassVar[UrlName]
    """URL for the page where users can bulk upload csv data."""

    create_url: ClassVar[UrlName]
    """URL for the page and where users can create individual model instances."""

    list_url: ClassVar[UrlName]
    """URL for the page listing instances of the given model, for a single school."""

    # Instance vars:
    school: models.School

    @abc.abstractmethod
    def has_existing_data(self) -> bool:
        """
        Whether the school currently has any data for the relevant model.
        The user won't be given the full management options if they don't have any data to manage.
        """
        raise NotImplemented

    def cannot_add_data_reason(self) -> str | None:
        """
        Whether the school currently has sufficient data to add data for this model.
        E.g. there must be some year groups before the school can add pupils.
        """
        return None

    def setup(
        self, request: AuthenticatedHttpRequest, *args: Any, **kwargs: Any
    ) -> None:
        super().setup(request, *args, **kwargs)
        if request.user.is_authenticated:
            self.school = self.request.user.profile.school

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Add some restrictive context for the template."""
        context = super().get_context_data(**kwargs)

        context["has_existing_data"] = self.has_existing_data()
        context["cannot_add_data_reason"] = self.cannot_add_data_reason()

        context["model_name_singular"] = self.model_class.Constant.human_string_singular
        context["model_name_plural"] = self.model_class.Constant.human_string_plural

        context["upload_url"] = self.upload_url.url()
        context["create_url"] = self.create_url.url()
        context["list_url"] = self.list_url.url()

        return context
