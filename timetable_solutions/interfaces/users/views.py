"""
Views relating to user authentication and registration.

User registration has the following steps:
Step 1 - provide basic details (name, email address, password etc.)
Step 2 - a pivot - either the user belongs to a school that is already registered at TTS (c) or must the must also
register their school
Step 3a - the user must also register themselves with the school
Step 3b - the user must provide a school access key to associate themselves with a school that is already registered.
"""

# Django imports
from django import http
from django.contrib import messages
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import login, logout, mixins
from django.contrib.auth import views as auth_views
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic

# Local application imports
from data import constants, models
from interfaces.constants import UrlName
from interfaces.users import forms


class Register(generic.FormView):
    """
    Step 1 of registering - entering personal details.
    """

    template_name = "users/register.html"
    form_class = forms.UserCreation
    success_url = UrlName.REGISTER_PIVOT.url(lazy=True)

    def setup(self, request: http.HttpRequest, *args: object, **kwargs: object) -> None:
        """
        Ensure authenticated users are logged out if trying to access the registration page.
        """
        super().setup(request, *args, **kwargs)
        if request.user.is_authenticated:
            logout(request)

    def form_valid(self, form: forms.UserCreation) -> http.HttpResponse:
        user = form.save()
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        return super().form_valid(form=form)


class SchoolRegisterPivot(generic.FormView):
    """
    Step 2 of registering - pivoting to registering a new school or the user to an existing school.
    """

    template_name = "users/register-school-pivot.html"
    form_class = forms.SchoolRegistrationPivot

    def form_valid(self, form: forms.SchoolRegistrationPivot) -> http.HttpResponse:
        if form.cleaned_data["existing_school"] == form.NewUserType.EXISTING:
            redirect_url = UrlName.PROFILE_REGISTRATION.url()
        else:
            redirect_url = UrlName.SCHOOL_REGISTRATION.url()
        return redirect(to=redirect_url)


class SchoolRegistration(generic.FormView):
    """
    Step 3a of registering - registering a new school.

    The user receives the `SCHOOL_ADMIN` role, making them an admin of the new school's data.
    """

    template_name = "users/register-school.html"
    form_class = forms.SchoolRegistration

    def form_valid(self, form: forms.SchoolRegistration) -> http.HttpResponse:
        """
        Create a new school and profile for the registering user.
        """
        school_name = form.cleaned_data.get("school_name")

        with transaction.atomic():
            new_school = models.School.create_new(school_name=school_name)
            models.Profile.create_new(
                user=self.request.user,
                school_id=new_school.school_access_key,
                role=constants.UserRole.SCHOOL_ADMIN,  # type: ignore  # mypy thinks this is a tuple of int, list
                approved_by_school_admin=True,
            )

        message = f"Thanks for registering {school_name} at timetable solutions!"
        messages.success(self.request, message=message)
        return redirect(reverse(UrlName.DASHBOARD.value))


class ProfileRegistration(generic.FormView):
    """
    Step 3b of registering - registering a user to an existing school.

    The user must provide a valid school access key, and even succeeding this they are not granted
    access to the site until a school admin approves their account.
    """

    template_name = "users/register-profile-existing-school.html"
    form_class = forms.ProfileRegistration
    success_url = UrlName.LOGIN.url(lazy=True)

    def form_valid(self, form: forms.ProfileRegistration) -> http.HttpResponse:
        """
        Create a profile linking the user to an existing school.
        """
        access_key = form.cleaned_data.get("school_access_key")
        role = form.cleaned_data.get("position")

        models.Profile.create_new(
            user=self.request.user,
            school_id=access_key,
            role=role,
            approved_by_school_admin=False,
        )

        message = (
            "Registration successful!\n"
            "You will need to wait for your school admin to approve your account before gaining access to "
            "the site."
        )
        messages.success(self.request, message=message)
        return super().form_valid(form=form)


class Login(auth_views.LoginView):
    """
    Add some extra rules to the login process.
    """

    def setup(self, request: http.HttpRequest, *args: object, **kwargs: object) -> None:
        """
        Log a user out if they visit the login page.
        """
        super().setup(request, *args, **kwargs)
        if request.user.is_authenticated:
            logout(request)

    def form_valid(self, form: auth_forms.AuthenticationForm) -> http.HttpResponse:
        user = form.get_user()
        if not hasattr(user, "profile"):
            # The user has not completed registration
            login(
                self.request, user, backend="django.contrib.auth.backends.ModelBackend"
            )
            return redirect(to=UrlName.REGISTER_PIVOT.url())
        elif user.profile.approved_by_school_admin:
            return super().form_valid(form)
        else:
            error_message = (
                "Your account has not yet been approved by your school's admin account.\n"
                "Please contact them directly to approve your account."
            )
            form.add_error(None, error_message)
            return super().form_invalid(form=form)


def custom_logout(request: http.HttpResponse) -> http.HttpResponseRedirect:
    """
    Redirect users to the login page when they log out.
    """
    if request.user.is_authenticated:
        logout(request)
    return redirect(UrlName.LOGIN.url())


class PasswordChange(auth_views.PasswordChangeView):
    success_url = UrlName.DASHBOARD.url(lazy=True)

    def form_valid(self, form: auth_forms.PasswordChangeForm) -> http.HttpResponse:
        message = "Your password has been updated!"
        messages.success(request=self.request, message=message)
        return super().form_valid(form=form)


class Dashboard(mixins.LoginRequiredMixin, generic.TemplateView):
    template_name = "users/dashboard.html"
