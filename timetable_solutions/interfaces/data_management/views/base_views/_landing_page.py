# Standard library imports
import abc
from typing import Any, ClassVar

# Django imports
from django.contrib.auth import mixins
from django.views import generic

# Local application imports
from data import models
from interfaces.constants import UrlName


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

    @abc.abstractmethod
    def has_existing_data(self) -> bool:
        """
        Whether the school currently has any data for the relevant model.
        The user won't be given the full management options if they don't have any data to manage.
        """
        raise NotImplemented

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Add some restrictive context for the template."""
        context = super().get_context_data(**kwargs)

        context["has_existing_data"] = self.has_existing_data()

        context["model_name_singular"] = self.model_class.Constant.human_string_singular
        context["model_name_plural"] = self.model_class.Constant.human_string_plural

        context["upload_url"] = self.upload_url.url()
        context["create_url"] = self.create_url.url()
        context["list_url"] = self.list_url.url()

        return context
