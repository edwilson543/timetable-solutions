# Standard library imports
from typing import Any

# Django imports
from django import http
from django.contrib.auth import mixins
from django.contrib.auth import models as auth_models
from django.core import exceptions as django_exceptions
from django.views import generic

# Local application imports
from domain.users import operations
from interfaces.constants import UrlName
from interfaces.users import forms, serializers
from interfaces.utils import base_views
from interfaces.utils.typing_utils import AuthenticatedHttpRequest


class UserProfileList(mixins.LoginRequiredMixin, generic.ListView):
    """
    List all users and profiles of this school.
    """

    template_name = "user-management/user-list.html"
    ordering = ["username"]
    paginate_by = 50
    http_method_names = ["get"]

    serializer_class = serializers.UserProfile

    displayed_fields = {
        "username": "Username",
        "first_name": "Firstname",
        "last_name": "Surname",
        "email": "Email",
        "approved_by_school_admin": "Approved",
        "role": "Role",
    }

    # Instance vars
    school_id: int

    def setup(
        self, request: AuthenticatedHttpRequest, *args: object, **kwargs: object
    ) -> None:
        """Set some instance attributes used in later logic."""
        super().setup(request, *args, **kwargs)
        self.school_id = request.user.profile.school.school_access_key

    def get_queryset(self) -> list[dict]:
        """Retrieve all the school's data for this model."""
        queryset = auth_models.User.objects.prefetch_related("profile").filter(
            profile__school_id=self.school_id
        )
        queryset = queryset.order_by(*self.ordering)
        return self.serializer_class(queryset, many=True).data

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """
        Include a queryset in the context.

        This is either the return of the user's search, or all model data for their school.
        """
        context = super().get_context_data(**kwargs)
        context["displayed_fields"] = self.displayed_fields
        context["model_name_singular"] = "user"
        context["model_name_plural"] = "users"
        return context


class UpdateUserProfile(base_views.UpdateView[auth_models.User, forms.UpdateUser]):
    """
    Display information on a single user, and allow this data to be updated / deleted.
    """

    template_name = "user-management/user-detail-update.html"

    model_class = auth_models.User
    form_class = forms.UpdateUser
    serializer_class = serializers.UserProfile

    object_id_name = "username"

    page_url_prefix = UrlName.USER_UPDATE
    delete_success_url = UrlName.USER_LIST.url(lazy=True)

    def setup(
        self, request: AuthenticatedHttpRequest, *args: object, **kwargs: Any
    ) -> None:
        super().setup(request, *args, **kwargs)
        client_profile = request.user.profile
        if not client_profile.is_school_admin:
            raise django_exceptions.PermissionDenied()
        target_user_profile = self.model_instance.profile

        # The username is the kwarg, so we need to explicitly stop
        # users managing other school's users
        if not client_profile.school == target_user_profile.school:
            raise django_exceptions.PermissionDenied()

    def update_model_from_clean_form(self, form: forms.UpdateUser) -> auth_models.User:
        """
        Update a user and their profile in the db.
        """
        first_name = form.cleaned_data.get("first_name", None)
        last_name = form.cleaned_data.get("last_name", None)
        email = form.cleaned_data.get("email", None)
        approved_by_school_admin = form.cleaned_data.get(
            "approved_by_school_admin", None
        )
        role = form.cleaned_data.get("role", None)
        return operations.update_user(
            user=self.model_instance,
            first_name=first_name,
            last_name=last_name,
            email=email,
            approved_by_school_admin=approved_by_school_admin,
            role=role,
        )

    def delete_model_instance(self) -> None:
        """
        Delete the User stored as an instance attribute.
        """
        operations.delete_user(user=self.model_instance)

    def _get_object_or_404(self, model_instance_id: int | str) -> auth_models.User:
        """
        Retrieve the user we are updating.
        """
        try:
            return auth_models.User.objects.prefetch_related("profile").get(
                username=self.model_instance_id
            )
        except auth_models.User.DoesNotExist:
            raise http.Http404

    def _get_initial_form_kwargs(self) -> dict[str, Any]:
        return {
            "first_name": self.model_instance.first_name,
            "last_name": self.model_instance.last_name,
            "email": self.model_instance.email,
            "approved_by_school_admin": self.model_instance.profile.approved_by_school_admin,
            "role": self.model_instance.profile.role,
        }

    def get_form_kwargs(self) -> dict[str, Any]:
        """Add the model instance to the form kwargs so the values can be set as initials."""
        kwargs = super(base_views.UpdateView, self).get_form_kwargs()
        kwargs["initial"] = {
            "first_name": self.model_instance.first_name,
            "last_name": self.model_instance.last_name,
            "email": self.model_instance.email,
            "approved_by_school_admin": self.model_instance.profile.approved_by_school_admin,
            "role": self.model_instance.profile.role,
        }
        if not self.is_update_request:
            # Do not bind any data or files to this form
            kwargs.pop("data", None)
            kwargs.pop("files", None)
        return kwargs
