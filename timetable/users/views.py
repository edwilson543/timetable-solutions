# Standard library imports
from typing import Dict

# Django imports
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse

# Local application imports
from .models import Profile
from .forms import CustomUserCreationForm, SchoolRegistrationPivot, SchoolRegistrationForm, ProfileRegistrationForm


# Create your views here.
class Register(View):
    """View for step 1 of registering - entering basic details."""
    @staticmethod
    def get(request, context: Dict | None = None):
        if context is None:
            context = {"form": CustomUserCreationForm}
        if request.user.is_authenticated:
            logout(request)
        return render(request, "users/register.html", context)

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("registration_pivot"))
        else:
            context = {
                "error_messages": form.error_messages,
                "form": CustomUserCreationForm
            }
            return self.get(request, context=context)


class SchoolRegisterPivot(View):
    """View for step 2 of registering - whether or not school also needs registering"""

    @staticmethod
    def get(request, context: Dict | None = None):
        if context is None:
            context = {"form": SchoolRegistrationPivot}
        return render(request, "users/register_school_pivot.html", context)

    @staticmethod
    def post(request):
        form = SchoolRegistrationPivot(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("existing_school") == "EXISTING":
                return redirect(reverse("profile_registration"))
            else:
                return redirect(reverse("school_registration"))
        else:
            return redirect(reverse("register"))


class SchoolRegistration(View):
    """View for step 3a of registering - when the school is not registered"""

    @staticmethod
    def get(request, context: Dict | None = None):
        if context is None:
            context = {"form": SchoolRegistrationForm}
        return render(request, "users/register_school.html", context)

    def post(self, request):
        form = SchoolRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Note this is a model form
            return redirect(reverse("dashboard"))
        else:
            context = {
                "form": SchoolRegistrationForm,
                "error_message": form.error_message,
            }
            return self.get(request, context)


class ProfileRegistration(View):
    """View for step 3b of registering - when the school is already registered, just need the access key"""

    @staticmethod
    def get(request, context: Dict | None = None):
        if context is None:
            context = {"form": ProfileRegistrationForm}
        return render(request, "users/register_profile_existing_school.html", context)

    def post(self, request):
        form = ProfileRegistrationForm(request.POST)
        if form.is_valid():
            access_key = form.cleaned_data.get("school_access_key")
            # noinspection PyUnresolvedReferences
            profile = Profile.objects.create(user=request.user, school_id=access_key)
            profile.save()
            return redirect(reverse("dashboard"))
        else:
            context = {
                "form": ProfileRegistrationForm,
                "error_message": form.error_message,
            }
            return self.get(request, context=context)


def custom_logout(request):
    """
    View redirecting users to the login page when they logout rather than the dashboard, since there is no
    application unless the user is logged in.
    """
    logout(request)
    return redirect(reverse("login"))


def dashboard_view(request):
    """
    Method to add some context to the dashboard view, for rendering in the template.
    This is to restrict the list of options available to users.
    """
    if not request.user.is_authenticated:
        return redirect(reverse("login"))

    return render(request, "users/dashboard.html")
