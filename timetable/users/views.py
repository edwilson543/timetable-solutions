# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse
from django.views import View
from .forms import CustomUserCreationForm, SchoolRegistrationPivot, SchoolRegistrationForm, ProfileRegistrationForm

# Local application imports
from .models import Profile


# Create your views here.
class Register(View):
    """View for step 1 of registering - entering basic details."""
    @staticmethod
    def get(request):
        return render(
            request, "users/register.html",
            {"form": CustomUserCreationForm}
        )

    @staticmethod
    def post(request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return SchoolRegisterPivot.get(request)


class SchoolRegisterPivot(View):
    """View for step 2 of registering - whether or not school also needs registering"""

    @staticmethod
    def get(request):
        return render(
            request, "users/register_school_pivot.html",
            {"form": SchoolRegistrationPivot}
        )

    @staticmethod
    def post(request):
        form = SchoolRegistrationPivot(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("existing_school") == "EXISTING":
                return ProfileRegistration.get(request)
            else:
                return SchoolRegistration.get(request)


class SchoolRegistration(View):
    """View for step 3a of registering - when the school is not registered"""

    @staticmethod
    def get(request):
        return render(
            request, "users/register_school.html",
            {"form": SchoolRegistrationForm}
        )

    @staticmethod
    def post(request):
        form = SchoolRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Note this is a model form
            return redirect(reverse("dashboard"))
        else:
            # TODO - create an error message
            pass


class ProfileRegistration(View):
    """View for step 3b of registering - when the school is already registered, just need the access key"""

    @staticmethod
    def get(request):
        return render(
            request, "users/school_access_key.html",
            {"form": ProfileRegistrationForm}
        )

    @staticmethod
    def post(request):
        form = ProfileRegistrationForm(request.POST)
        if form.is_valid():
            access_key = form.cleaned_data.get("school_access_key")
            profile = Profile(user=request.user, school=access_key)
            profile.save()
            return redirect(reverse("dashboard"))
        else:
            # TODO - access key not found message
            pass
