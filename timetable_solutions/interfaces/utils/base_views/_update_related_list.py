# Standard library imports
import abc
from typing import Any, ClassVar

# Django imports
from django import forms as django_forms
from django import http
from django.views.generic import edit

# Local application imports
from domain.data_management import base_exceptions
from interfaces.utils.base_views import _related_list
from interfaces.utils.typing_utils import AuthenticatedHttpRequest


class UpdateRelatedListPartialView(
    _related_list.RelatedListPartialView[
        _related_list.ModelT, _related_list.RelatedModelT
    ],
    edit.BaseFormView,
):
    """
    View allowing adding and removing related objects to a single model instance.

    The BaseFormView is included in the MRO to allow adding relating objects.
    For removing related object, the DELETE http method is handled.

    Note that all requests to this view are submitted via htmx.
    """

    form_class: type[django_forms.Form]
    """Form used to add a related object to the model instance."""

    related_object_id_name: ClassVar[str]
    """Name of the related object's id field."""

    related_model_class: type[_related_list.RelatedModelT]
    """The model class of the object we are trying to delete."""

    @abc.abstractmethod
    def add_related_object(self, form: django_forms.Form) -> None:
        """
        Add a related object to the target object's related object list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def remove_related_object(
        self, related_model_instance: _related_list.RelatedModelT
    ) -> None:
        """
        Remove a related object from the target object's related object list.
        """
        raise NotImplementedError

    def _get_success_response(self) -> http.HttpResponse:
        """
        Since this is an HTMX view, following a successful add or remove operation
        we just re-render the partial with the updated context, rather than
        redirecting to some new page as in an ordinary form view.
        """
        # Update the object list with the added relation
        self.object_list = super().get_queryset()
        form = self.form_class(**self.extra_form_kwargs())
        context = self.get_context_data(form=form)
        return super().render_to_response(context=context)

    # --------------------
    # Add related object (using POST and django form view)
    # --------------------

    def form_valid(self, form: django_forms.Form) -> http.HttpResponse:
        """
        Try updating the target object.
        """
        try:
            self.add_related_object(form=form)
        except base_exceptions.UnableToUpdateModelInstance as exc:
            form.add_error(field=None, error=exc.human_error_message)
            return self.form_invalid(form=form)
        return self._get_success_response()

    def form_invalid(self, form: django_forms.Form) -> http.HttpResponse:
        """
        Get the response when the form is not valid.
        """
        self.object_list = super().get_queryset()
        context = self.get_context_data(form=form)
        return super().render_to_response(context=context)

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """
        Add the form context.
        """
        context = super().get_context_data(**kwargs)
        # Include and rename the form
        context["add_form"] = kwargs.get("form", None) or self.get_form()
        return context

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Combine the default and custom form instantiation kwargs.
        """
        return super().get_form_kwargs() | self.extra_form_kwargs()

    def extra_form_kwargs(self) -> dict[str, Any]:
        """
        Hook for extra kwargs to use when instantiating a form.

        These are also used in _get_success_response, hence why they're
        not just added to get_form_kwargs().
        """
        return {}

    # --------------------
    # Remove related object
    # --------------------

    def delete(
        self, request: AuthenticatedHttpRequest, *args: object, **kwargs: object
    ) -> http.HttpResponse:
        """
        Handle the removal of a related object.

        Each row in the related object table has a single button form that fires
        a hx-delete request. A hidden input widget is used to specify the relevant
        related object that row should target.
        """
        related_model_instance = self._get_related_object_to_remove()
        try:
            self.remove_related_object(related_model_instance=related_model_instance)
            return self._get_success_response()
        except base_exceptions.UnableToUpdateModelInstance as exc:
            # Show the error on the add form as this makes the most sense visually
            form = self.form_class(**self.extra_form_kwargs())
            form.add_error(None, exc.human_error_message)
            return self.form_invalid(form=form)

    def _get_related_object_to_remove(self) -> _related_list.RelatedModelT:
        """
        Get the related object to move based on the POST kwarg.

        Note we don't use a django form since there would be no fields - all
        we'd be doing is extracting the related object id from the selection,
        hence the unconventional/unrecommended direct hit on POST.

        This approach avoids having to have another endpoint just for removal.
        """
        delete_request = http.QueryDict(self.request.body)
        related_object_id = delete_request["related-object-id"]
        return self.related_model_class.objects.get(
            school_id=self.school_id,
            **{self.related_object_id_name: related_object_id},
        )
