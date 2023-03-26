# Standard library imports
import abc
from typing import Any

# Django imports
from django import forms as django_forms
from django import http
from django.views.generic import edit

# Local application imports
from domain.data_management import base_exceptions
from interfaces.utils.base_views import _related_list


class UpdateRelatedListPartialView(
    _related_list.RelatedListPartialView,
    edit.BaseFormView,
):
    """
    View allowing adding to a related objects for a single model instance.

    The BaseFormView is added to provide form handling functionality.
    """

    @abc.abstractmethod
    def update_model_from_clean_form(self, form: django_forms.Form) -> None:
        """
        Add to or delete an object from the target object's related object list.
        """
        raise NotImplementedError

    def form_valid(self, form: django_forms.Form) -> http.HttpResponse:
        """
        Try updating the target object.
        """
        try:
            self.update_model_from_clean_form(form=form)
        except base_exceptions.UnableToUpdateModelInstance as exc:
            form.add_error(field=None, error=exc.human_error_message)
            return super().form_invalid(form=form)
        return super().form_valid(form=form)

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """
        Add the form context.
        """
        context = super().get_context_data(**kwargs)
        # Include and rename the form
        context["add_form"] = kwargs.get("form", None) or self.get_form()
        return context
