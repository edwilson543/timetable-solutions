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
        return self._get_success_response()

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """
        Add the form context.
        """
        context = super().get_context_data(**kwargs)
        # Include and rename the form
        context["add_form"] = kwargs.get("form", None) or self.get_form()
        return context

    def _get_success_response(self) -> http.HttpResponse:
        """
        Since this is an HTMX view, following a successful form operation
        we just re-render the partial with the updated context, rather than
        redirecting to some new page as in an ordinary form view.
        """
        # Update the object list with the added relation
        self.object_list = super().get_queryset()
        form = self.form_class(**self.extra_form_kwargs())
        context = self.get_context_data(form=form)
        return super().render_to_response(context=context)

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Combine the default and custom form instantiation kwargs.
        """
        return super().get_form_kwargs() | self.extra_form_kwargs()

    def extra_form_kwargs(self) -> dict[str, Any]:
        """
        Some extra kwargs to use when instantiating a form.

        These are also used in the success response, hence why they're
        not just added to get_form_kwargs().
        """
        return {}
