# Django imports
from django.contrib.auth import login
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
    def get(request):
        context = {"form": CustomUserCreationForm}
        return render(request, "users/register.html", context)

    @staticmethod
    def post(request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return SchoolRegisterPivot.get(request)
        else:
            context = {
                "error_messages": form.error_messages,
                "form": CustomUserCreationForm
            }
            return render(request, "users/register.html", context)


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
        else:
            return redirect(reverse("register"))


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
            # noinspection PyUnresolvedReferences
            profile = Profile.objects.create(user=request.user, school_id=access_key)
            profile.save()
            return redirect(reverse("dashboard"))
        else:
            # TODO - access key not found message
            pass
